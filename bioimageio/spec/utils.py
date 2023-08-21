import traceback
from copy import deepcopy
from pathlib import PurePath
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
)
from urllib.parse import urljoin

import pydantic
from pydantic import HttpUrl
from pydantic_core import PydanticUndefined

import bioimageio.spec
from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal._constants import DISCOVER, ERROR, LATEST, VERSION, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal._package import fill_resource_package_content
from bioimageio.spec._internal._utils import extract_file_name, nest_dict_with_narrow_first_key
from bioimageio.spec._internal._validate import ValContext, get_validation_context
from bioimageio.spec._internal.base_nodes import ResourceDescriptionBase
from bioimageio.spec._resource_types import ResourceDescription
from bioimageio.spec.types import (
    LegacyValidationSummary,
    Loc,
    RawStringDict,
    RawStringMapping,
    RelativeFilePath,
    ValidationContext,
    ValidationError,
    ValidationSummary,
    ValidationWarning,
    WarningLevelName,
)


def get_supported_format_versions() -> Mapping[str, Tuple[str, ...]]:
    supported: Dict[str, List[str]] = {}
    for typ, rd_class in _iterate_over_rd_classes():
        format_versions = supported.setdefault(typ, [])
        ma, mi, pa = rd_class.implemented_format_version_tuple
        for p in range(pa + 1):
            format_versions.append(f"{ma}.{mi}.{p}")

    supported["model"].extend([f"0.3.{i}" for i in range(7)])  # model 0.3 can be converted
    return MappingProxyType({t: tuple(fv) for t, fv in supported.items()})


def _iterate_over_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in get_args(
        Union[
            get_args(application.AnyApplication)[0],  # type: ignore
            get_args(collection.AnyCollection)[0],  # type: ignore
            get_args(dataset.AnyDataset)[0],  # type: ignore
            get_args(generic.AnyGeneric)[0],  # type: ignore
            get_args(model.AnyModel)[0],  # type: ignore
            get_args(notebook.AnyNotebook)[0],  # type: ignore
        ]
    ):
        typ = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def _iterate_over_latest_rd_classes() -> Iterable[Tuple[str, Type[ResourceDescription]]]:
    for rd_class in [
        application.Application,
        collection.Collection,
        dataset.Dataset,
        generic.Generic,
        model.Model,
        notebook.Notebook,
    ]:
        typ: Any = rd_class.model_fields["type"].default
        if typ is PydanticUndefined:
            typ = "generic"

        assert isinstance(typ, str)
        yield typ, rd_class


def check_type_and_format_version(data: RawStringMapping) -> Tuple[str, str, str]:
    typ = data.get("type")
    if not isinstance(typ, str):
        raise TypeError(f"Invalid resource type '{typ}' of type {type(typ)}")

    fv = data.get("format_version")
    if not isinstance(fv, str):
        raise TypeError(f"Invalid format version '{fv}' of type {type(fv)}")

    if fv in get_supported_format_versions().get(typ, ()):
        use_fv = fv
    elif hasattr(bioimageio.spec, typ):
        # type is specialized...
        type_module = getattr(bioimageio.spec, typ)
        # ...and major/minor format version is unknown
        v_module = type_module  # use latest
        if fv.count(".") == 2:
            v_module_name = f"v{fv[:fv.rfind('.')].replace('.', '_')}"
            if hasattr(type_module, v_module_name):
                # ...and we know the major/minor format version (only patch is unknown)
                v_module = getattr(type_module, v_module_name)

        rd_class = getattr(v_module, typ.capitalize())
        assert issubclass(rd_class, ResourceDescriptionBase)
        use_fv = rd_class.implemented_format_version
    else:
        # fallback: type is not specialized (yet) and format version is unknown
        use_fv = bioimageio.spec.generic.Generic.implemented_format_version  # latest generic

    return typ, fv, use_fv


def get_rd_class(type_: str, /, format_version: str = LATEST) -> Union[Type[ResourceDescription], str]:
    """Get the appropriate resource description class for a given `type` and `format_version`.

    returns:
        resource description class
        or string with error message

    """
    assert isinstance(format_version, str)
    if format_version != LATEST and format_version.count(".") == 0:
        format_version = format_version + ".0"
    elif format_version.count(".") == 2:
        format_version = format_version[: format_version.rfind(".")]

    rd_classes: Dict[str, Dict[str, Type[ResourceDescription]]] = {}
    for typ, rd_class in _iterate_over_rd_classes():
        per_fv: Dict[str, Type[ResourceDescription]] = rd_classes.setdefault(typ, {})

        ma, mi, _pa = rd_class.implemented_format_version_tuple
        key = f"{ma}.{mi}"
        assert key not in per_fv
        per_fv[key] = rd_class

    for typ, rd_class in _iterate_over_latest_rd_classes():
        rd_classes[typ]["latest"] = rd_class

    rd_class = rd_classes.get(type_, rd_classes["generic"]).get(format_version)
    if rd_class is None:
        return f"{type_} (or generic) specification {format_version} does not exist."

    return rd_class


def update_format(
    resource_description: RawStringMapping,
    update_to_format: str = "latest",
    context: Optional[ValidationContext] = None,
) -> RawStringMapping:
    """Auto-update fields of a bioimage.io resource without any validation."""
    assert "type" in resource_description
    assert isinstance(resource_description["type"], str)
    rd_class = get_rd_class(resource_description["type"], update_to_format)
    if isinstance(rd_class, str):
        raise ValueError(rd_class)

    rd = dict(resource_description)
    val_context = get_validation_context(**(context or {}))
    rd_class.convert_from_older_format(rd, val_context)
    return rd


RD = TypeVar("RD", bound=ResourceDescriptionBase)


def dump_description(resource_description: ResourceDescription) -> RawStringDict:
    """Converts a resource to a dictionary containing only simple types that can directly be serialzed to YAML."""
    return resource_description.model_dump(mode="json", exclude={"root"})


def _load_descr_impl(rd_class: Type[RD], resource_description: RawStringMapping, context: ValContext):
    rd: Optional[RD] = None
    val_errors: List[ValidationError] = []
    val_warnings: List[ValidationWarning] = []
    tb: Optional[List[str]] = None

    try:
        rd = rd_class.model_validate(resource_description, context=dict(context))
    except pydantic.ValidationError as e:
        for ee in e.errors(include_url=False):
            if (type_ := ee["type"]) in get_args(WarningLevelName):
                val_warnings.append(ValidationWarning(loc=ee["loc"], msg=ee["msg"], type=type_))  # type: ignore
            else:
                val_errors.append(ValidationError(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))

    except Exception as e:
        val_errors.append(ValidationError(loc=(), msg=str(e), type=type(e).__name__))
        tb = traceback.format_tb(e.__traceback__)

    return rd, val_errors, tb, val_warnings


def load_description_with_known_rd_class(
    resource_description: RawStringMapping,
    *,
    context: Optional[ValidationContext] = None,
    rd_class: Type[RD],
) -> Tuple[Optional[RD], ValidationSummary]:
    val_context = get_validation_context(**(context or {}))

    raw_rd = deepcopy(dict(resource_description))
    rd, errors, tb, val_warnings = _load_descr_impl(
        rd_class,
        raw_rd,
        {**val_context, WARNING_LEVEL_CONTEXT_KEY: ERROR},
    )  # ignore any warnings using warning level 'ERROR'/'CRITICAL' on first loading attempt
    if rd is None:
        resource_type = rd_class.model_fields["type"].default
        format_version = rd_class.implemented_format_version
    else:
        resource_type = rd.type
        format_version = rd.format_version
        assert not errors, f"got rd, but also errors: {errors}"
        assert tb is None, f"got rd, but also an error traceback: {tb}"
        assert not val_warnings, f"got rd, but also already warnings: {val_warnings}"
        _, error2, tb2, val_warnings = _load_descr_impl(rd_class, raw_rd, val_context)
        assert not error2, f"increasing warning level caused errors: {error2}"
        assert tb2 is None, f"increasing warning level lead to error traceback: {tb2}"

    summary = ValidationSummary(
        bioimageio_spec_version=VERSION,
        errors=errors,
        name=f"bioimageio.spec static {resource_type} validation (format version: {format_version}).",
        source_name=(val_context["root"] / val_context["file_name"]).as_posix()
        if isinstance(val_context["root"], PurePath)
        else urljoin(str(val_context["root"]), val_context["file_name"]),
        status="failed" if errors else "passed",
        warnings=val_warnings,
    )
    if tb:
        summary["traceback"] = tb

    return rd, summary


def load_description(
    resource_description: RawStringMapping,
    *,
    context: Optional[ValidationContext] = None,
    format_version: Union[Literal["discover"], Literal["latest"], str] = DISCOVER,
) -> Tuple[Optional[ResourceDescription], ValidationSummary]:
    discovered_type, discovered_format_version, use_format_version = check_type_and_format_version(resource_description)
    if use_format_version != discovered_format_version:
        resource_description = dict(resource_description)
        resource_description["format_version"] = use_format_version
        future_patch_warning = ValidationWarning(
            loc=("format_version",),
            msg=f"Treated future patch version {discovered_format_version} as {use_format_version}.",
            type="alert",
        )
    else:
        future_patch_warning = None

    fv = use_format_version if format_version == DISCOVER else format_version
    rd_class = get_rd_class(discovered_type, format_version=fv)
    if isinstance(rd_class, str):
        rd = None
        val_context = get_validation_context(**(context or {}))
        root = val_context["root"]
        file_name = val_context["file_name"]
        summary = ValidationSummary(
            bioimageio_spec_version=VERSION,
            errors=[ValidationError(loc=(), msg=rd_class, type="error")],
            name=f"bioimageio.spec static {discovered_type} validation (format version: {format_version}).",
            source_name=(root / file_name).as_posix() if isinstance(root, PurePath) else urljoin(str(root), file_name),
            status="failed",
            warnings=[],
        )
    else:
        rd, summary = load_description_with_known_rd_class(resource_description, context=context, rd_class=rd_class)

    if future_patch_warning:
        summary["warnings"] = list(summary["warnings"]) if "warnings" in summary else []
        summary["warnings"].insert(0, future_patch_warning)

    return rd, summary


def validate(
    resource_description: RawStringMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: Optional[ValidationContext] = None,
    as_format: Union[Literal["discover", "latest"], str] = DISCOVER,
) -> ValidationSummary:
    _rd, summary = load_description(resource_description, context=context, format_version=as_format)
    return summary


def validate_legacy(
    resource_description: RawStringMapping,  # raw resource description (e.g. loaded from an rdf.yaml file).
    context: Optional[ValidationContext] = None,
    update_format: bool = False,  # apply auto-conversion to the latest type-specific format before validating.
) -> LegacyValidationSummary:
    """Validate a bioimage.io resource description returning the legacy validaiton summary.

    The legacy validation summary contains any errors and warnings as nested dict."""

    vs = validate(resource_description, context, LATEST if update_format else DISCOVER)

    error = vs["errors"]
    legacy_error = nest_dict_with_narrow_first_key({e["loc"]: e["msg"] for e in error}, first_k=str)
    tb = vs.get("traceback")
    tb_list = None if tb is None else list(tb)
    return LegacyValidationSummary(
        bioimageio_spec_version=vs["bioimageio_spec_version"],
        error=legacy_error,
        name=vs["name"],
        source_name=vs["source_name"],
        status=vs["status"],
        traceback=tb_list,
        warnings={".".join(map(str, w["loc"])): w["msg"] for w in vs["warnings"]} if "warnings" in vs else {},
    )


def prepare_to_package(
    rd: ResourceDescription,
    *,
    weights_priority_order: Optional[Sequence[str]] = None,  # model only
    package_urls: bool = True,
) -> Tuple[ResourceDescription, Dict[str, Union[HttpUrl, RelativeFilePath]]]:
    """
    Args:
        rd: resource description
        # for model resources only:
        weights_priority_order: If given, only the first weights format present in the model is included.
                                If none of the prioritized weights formats is found a ValueError is raised.

    Returns:
        Modified resource description copy and associated package content mapping file names to URLs or local paths,
        which are referenced in the modfieid resource description.
        Important note: The serialized resource description itself (= an rdf.yaml file) is not included.
    """
    if weights_priority_order is not None and isinstance(rd, get_args(model.AnyModel)):
        # select single weights entry
        for w in weights_priority_order:
            weights_entry: Any = rd.weights.get(w)  # type: ignore
            if weights_entry is not None:
                rd = rd.model_copy(update=dict(weights={w: weights_entry}))
                break
        else:
            raise ValueError("None of the weight formats in `weights_priority_order` is present in the given model.")

    package_content: Dict[Loc, Union[HttpUrl, RelativeFilePath]] = {}
    fill_resource_package_content(package_content, rd, node_loc=(), package_urls=package_urls)
    file_names: Dict[Loc, str] = {}
    file_sources: Dict[str, Union[HttpUrl, RelativeFilePath]] = {}
    for loc, src in package_content.items():
        file_name = extract_file_name(src)
        if file_name in file_sources and file_sources[file_name] != src:
            for i in range(2, 10):
                fn, *ext = file_name.split(".")
                alternative_file_name = ".".join([f"{fn}_{i}", *ext])
                if alternative_file_name not in file_sources or file_sources[alternative_file_name] == src:
                    file_name = alternative_file_name
                    break
            else:
                raise RuntimeError(f"Too many file name clashes for {file_name}")

        file_sources[file_name] = src
        file_names[loc] = file_name

    # update resource description to point to local files
    rd = rd.model_copy(update=nest_dict_with_narrow_first_key(file_names, str))

    return rd, file_sources


def format_summary(summary: ValidationSummary):
    def format_loc(loc: Tuple[Union[int, str], ...]) -> str:
        if not loc:
            loc = ("root",)

        return ".".join(f"({x})" if x[0].isupper() else x for x in map(str, loc))

    es = "\n    ".join(
        e if isinstance(e, str) else f"{format_loc(e['loc'])}: {e['msg']}" for e in summary["errors"] or []
    )
    ws = "\n    ".join(f"{format_loc(w['loc'])}: {w['msg']}" for w in summary["warnings"])

    es_msg = f"errors: {es}" if es else ""
    ws_msg = f"warnings: {ws}" if ws else ""

    return f"{summary['name'].strip('.')}: {summary['status']}\nsource: {summary['source_name']}\n{es_msg}\n{ws_msg}"
