# type: ignore  # all sorts of unbound types :)
from __future__ import annotations

import dataclasses
import os
import pathlib
import warnings
from abc import ABC, abstractmethod
from copy import deepcopy
from io import StringIO
from typing import Any, ClassVar, Dict, Optional, Sequence, TYPE_CHECKING, Type, TypeVar, Union
from zipfile import ZipFile

from marshmallow import ValidationError, missing

from . import nodes, raw_nodes
from .common import BIOIMAGEIO_CACHE_PATH, NoOverridesDict, Protocol, get_args, yaml
from .raw_nodes import ImportableSourceFile, Node
from .schema import SharedBioImageIOSchema
from .utils import (
    GenericNode,
    PathToRemoteUriTransformer,
    get_dict_and_root_path_from_yaml_source,
    resolve_local_uri,
    resolve_raw_node_to_node,
    resolve_uri,
)

if TYPE_CHECKING:
    import bioimageio.spec as current_spec

# placeholders for versioned classes
ModelSchema = TypeVar("ModelSchema", bound=SharedBioImageIOSchema)
RawModelNode = TypeVar("RawModelNode", bound=raw_nodes.Node)
ModelNode = TypeVar("ModelNode", bound=nodes.Node)


# placeholders for versioned modules
class ConvertersModule(Protocol):
    def maybe_convert_model(self, data: dict) -> dict:
        raise NotImplementedError


class RawNodesModule(Protocol):
    ModelFormatVersion: Any
    Model: Type[RawModelNode]


class NodesModule(Protocol):
    Model: Type[RawModelNode]


class SchemaModule(Protocol):
    Model: Type[ModelSchema]


# class IO_Meta(ABCMeta):
#     """
#     defines abstract class properties for IO_Interface
#     """
#
#     @property
#     @abstractmethod
#     def preceding_io_class(self) -> IO_Base:
#         raise NotImplementedError


# IO interface to clarify intention of IO classes
# class IO_Interface(metaclass=IO_Meta):
class IO_Interface(ABC):
    """
    bioimageio.spec has submodules for each minor format version to validate and work with previously released
    format versions. To share io code across versions the IO_Base class implements format version independent io
    utilities.
    """

    # modules with format version specific implementations of schema, nodes, etc.
    # todo: 'real' abstract class properties for IO_Interface. see IO_Meta draft above
    preceding_io_class: ClassVar[Optional[IO_Base]]
    converters: ClassVar[ConvertersModule]
    schema: ClassVar[SchemaModule]
    raw_nodes: ClassVar[RawNodesModule]
    nodes: ClassVar[RawNodesModule]

    #
    # delegate format version
    #
    @classmethod
    def get_matching_io_class(cls, data_version: str, action_descr: str):
        """
        traverses preceding io classes to find IO class that matches 'data_version'.
        This function allows to select the appropriate format specific implementation for a given source.
        IO classes are not aware of any future format versions, only the one preceding itself.
        See IO_Base.load_raw_model() for example use.
        """
        raise NotImplementedError

    @staticmethod
    def get_version_tuple_wo_patch(version: str):
        """Extract (MAJOR, MINOR) from strict version string 'MARJO.MINOR.PATCH'."""
        raise NotImplementedError

    @classmethod
    def get_current_format_version_wo_patch(cls):
        """Return (MAJOR, MINOR) of IO 'cls'."""
        raise NotImplementedError

    #
    # io for model RDFs
    #   raw model
    #
    @classmethod
    @abstractmethod
    def load_raw_model(
        cls, source: Union[os.PathLike, str, dict, raw_nodes.URI], update_to_current_format: bool = False
    ) -> RawModelNode:
        raise NotImplementedError

    @classmethod
    def ensure_raw_model(
        cls,
        raw_model: Union[str, dict, os.PathLike, raw_nodes.URI, RawModelNode],
        root_path: os.PathLike,
        update_to_current_format: bool,
    ):
        raise NotImplementedError

    @classmethod
    def maybe_convert_model(cls, data: dict):
        """
        If model 'data' is specified in a preceding format this function converts it to the 'current' format of this
        IO class. Note: In an IO class of a previous format version, this is not the overall latest format version.
        The 'current' format version is determined by IO_Base.get_matching_io_class() and may be overwritten if
        'update_to_current_format'--an argument used in several IO methods--is True.
        """
        raise NotImplementedError

    @classmethod
    def serialize_raw_model_to_dict(cls, raw_model: RawModelNode) -> dict:
        """Serialize a `raw_nodes.Model` object with marshmallow to a plain dict with only basic data types"""
        raise NotImplementedError

    @classmethod
    def serialize_raw_model(cls, raw_model: Union[dict, RawModelNode]) -> str:
        """Serialize a raw model to a yaml string"""
        raise NotImplementedError

    @classmethod
    def save_raw_model(cls, raw_model: RawModelNode, path: pathlib.Path) -> None:
        """Serialize a raw model to a new yaml file at 'path'"""
        raise NotImplementedError

    #
    #   (evaluated) model
    #
    @classmethod
    def load_model(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        update_to_current_format: bool = True,
    ) -> ModelNode:
        """
        Load a `nodes.Model` object from a model RDF 'source'.
        nodes.Model objects hold all model RDF information as ready-to-use python objects,
        e.g. with locally available weights files and imported source code identifiers
        """
        raise NotImplementedError

    #
    # packaging
    #
    @classmethod
    def get_package_content(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict],
        root_path: pathlib.Path,
        update_to_current_format: bool = False,
        weights_formats_priorities: Optional[Sequence[str]] = None,
    ) -> Dict[str, Union[str, pathlib.Path]]:
        """Gather content required for exporting a bioimage.io package from an RDF source."""
        raise NotImplementedError

    @classmethod
    def export_package(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        update_to_current_format: bool = False,
        weights_formats_priorities: Optional[Sequence[current_spec.raw_nodes.WeightsFormat]] = None,
    ) -> pathlib.Path:
        """Export a bioimage.io package from an RDF source."""
        raise NotImplementedError


class IO_Base(IO_Interface):
    @classmethod
    def load_raw_model(
        cls, source: Union[os.PathLike, str, dict, raw_nodes.URI], update_to_current_format: bool = False
    ) -> RawModelNode:
        if isinstance(source, dict):
            data = source
        else:
            source = resolve_local_uri(source, pathlib.Path())
            data, root_path = get_dict_and_root_path_from_yaml_source(source)

        if update_to_current_format:
            io_cls = cls
        else:
            io_cls = cls.get_matching_io_class(data.get("format_version"), "load")

        data = io_cls.maybe_convert_model(data)
        raw_model: RawModelNode = io_cls._load_raw_model_from_dict_wo_format_conv(data)

        if isinstance(source, raw_nodes.URI):
            # for a remote source relative paths are invalid; replace all relative file paths in source with URLs
            warnings.warn(
                f"changing file paths in model RDF to URIs due to a remote {source.scheme} source "
                "(may result in invalid model)"
            )
            raw_model = PathToRemoteUriTransformer(remote_source=source).transform(raw_model)

        assert isinstance(raw_model, io_cls.raw_nodes.Model)
        return raw_model

    @classmethod
    def serialize_raw_model_to_dict(cls, raw_model: RawModelNode) -> dict:
        io_cls = cls.get_matching_io_class(raw_model.format_version, "serialize")
        serialized = io_cls.schema.Model().dump(raw_model)
        assert isinstance(serialized, dict)
        return serialized

    @classmethod
    def save_raw_model(cls, raw_model: RawModelNode, path: pathlib.Path):
        warnings.warn("only saving serialized rdf, no associated resources.")
        if path.suffix != ".yaml":
            warnings.warn("saving with '.yaml' suffix is strongly encouraged.")

        serialized = cls.serialize_raw_model_to_dict(raw_model)
        yaml.dump(serialized, path)

    @classmethod
    def serialize_raw_model(cls, raw_model: Union[dict, RawModelNode]) -> str:
        if not isinstance(raw_model, dict):
            raw_model = cls.serialize_raw_model_to_dict(raw_model)

        with StringIO() as stream:
            yaml.dump(raw_model, stream)
            return stream.getvalue()

    @classmethod
    def load_model(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        update_to_current_format: bool = True,
    ):
        raw_model, root_path = cls.ensure_raw_model(source, root_path, update_to_current_format)

        matching_cls = cls.get_matching_io_class(raw_model.format_version, "load")

        model: ModelNode = resolve_raw_node_to_node(
            raw_node=raw_model, root_path=pathlib.Path(root_path), nodes_module=matching_cls.nodes
        )
        assert isinstance(model, matching_cls.nodes.Model)

        return model

    @classmethod
    def export_package(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict, raw_nodes.URI],
        root_path: os.PathLike = pathlib.Path(),
        update_to_current_format: bool = False,
        weights_formats_priorities: Optional[Sequence[current_spec.raw_nodes.WeightsFormat]] = None,
    ) -> pathlib.Path:
        """
        weights_formats_priorities: If given only the first matching weights format present in the model is included.
                                    If none of the prioritized weights formats is found all are included.
        """
        raw_model, root_path = cls.ensure_raw_model(source, root_path, update_to_current_format)
        io_cls = cls.get_matching_io_class(raw_model.format_version, "export")
        package_path = io_cls._make_package_wo_format_conv(
            raw_model, root_path, weights_formats_priorities=weights_formats_priorities
        )
        return package_path

    @classmethod
    def _make_package_wo_format_conv(
        cls, raw_model: RawModelNode, root_path: os.PathLike, weights_formats_priorities: Optional[Sequence[str]]
    ):
        package_file_name = raw_model.name
        if raw_model.version is not missing:
            package_file_name += f"_{raw_model.version}"

        package_file_name = package_file_name.replace(" ", "_").replace(".", "_")

        BIOIMAGEIO_CACHE_PATH.mkdir(exist_ok=True, parents=True)
        package_path = (BIOIMAGEIO_CACHE_PATH / package_file_name).with_suffix(".zip")
        max_cached_packages_with_same_name = 100
        for p in range(max_cached_packages_with_same_name):
            if package_path.exists():
                package_path = (BIOIMAGEIO_CACHE_PATH / f"{package_file_name}p{p}").with_suffix(".zip")
            else:
                break
        else:
            raise FileExistsError(
                f"Already caching {max_cached_packages_with_same_name} versions of {BIOIMAGEIO_CACHE_PATH / package_file_name}!"
            )
        package_content = cls._get_package_content_wo_format_conv(
            deepcopy(raw_model), root_path=root_path, weights_formats_priorities=weights_formats_priorities
        )
        cls.make_zip(package_path, package_content)
        return package_path

    @classmethod
    def get_package_content(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict],
        root_path: pathlib.Path,
        update_to_current_format: bool = False,
        weights_formats_priorities: Optional[Sequence[str]] = None,
    ) -> Dict[str, Union[str, pathlib.Path]]:
        """
        weights_formats_priorities: If given only the first weights format present in the model is included.
                                    If none of the prioritized weights formats is found all are included.
        """
        raw_model, root_path = cls.ensure_raw_model(source, root_path, update_to_current_format)
        io_cls = cls.get_matching_io_class(raw_model.format_version, "get the package content of")
        package_content = io_cls._get_package_content_wo_format_conv(
            deepcopy(raw_model), root_path=root_path, weights_formats_priorities=weights_formats_priorities
        )
        return package_content

    @classmethod
    def _get_package_content_wo_format_conv(
        cls,
        raw_model: current_spec.raw_nodes.Model,
        root_path: os.PathLike,
        weights_formats_priorities: Optional[Sequence[str]],
    ) -> Dict[str, Union[str, pathlib.Path]]:
        package = NoOverridesDict(
            key_exists_error_msg="Package content conflict for {key}"
        )  # todo: add check in model validation
        package["original_rdf.txt"] = cls.serialize_raw_model(raw_model)  # todo: .txt -> .yaml once 'rdf.yaml' is only valid rdf file name in package

        def incl_as_local(node: GenericNode, field_name: str) -> GenericNode:
            value = getattr(node, field_name)
            if value is not missing:
                if isinstance(value, list):
                    fps = [resolve_uri(v, root_path=root_path) for v in value]
                    for fp in fps:
                        package[fp.name] = fp

                    new_field_value = [pathlib.Path(fp.name) for fp in fps]
                else:
                    fp = resolve_uri(value, root_path=root_path)
                    package[fp.name] = fp
                    new_field_value = pathlib.Path(fp.name)

                node = dataclasses.replace(node, **{field_name: new_field_value})

            return node

        raw_model = incl_as_local(raw_model, "documentation")
        raw_model = incl_as_local(raw_model, "test_inputs")
        raw_model = incl_as_local(raw_model, "test_outputs")
        raw_model = incl_as_local(raw_model, "covers")

        # todo: improve dependency handling
        if raw_model.dependencies is not missing:
            manager, fp = raw_model.dependencies.split(":")
            fp = resolve_uri(fp, root_path=root_path)
            package[fp.name] = fp
            raw_model = dataclasses.replace(raw_model, dependencies=f"{manager}:{fp.name}")

        if isinstance(raw_model.source, ImportableSourceFile):
            source = incl_as_local(raw_model.source, "source_file")
            raw_model = dataclasses.replace(raw_model, source=source)

        # filter weights
        for wfp in weights_formats_priorities or []:
            if wfp in raw_model.weights:
                weights = {wfp: raw_model.weights[wfp]}
                break
        else:
            weights = raw_model.weights

        # add weights
        local_weights = {}
        for wf, weights_entry in weights.items():
            weights_entry = incl_as_local(weights_entry, "source")
            local_files = []
            if weights_entry.attachments is not missing:
                for fa in weights_entry.attachments.get("files", []):
                    fa = resolve_uri(fa, root_path=root_path)
                    package[fa.name] = fa
                    local_files.append(fa.name)

            if local_files:
                weights_entry.attachments["files"] = local_files

            local_weights[wf] = weights_entry

        raw_model = dataclasses.replace(raw_model, weights=local_weights)

        # attachments:files
        if raw_model.attachments is not missing:
            local_files = []
            for fa in raw_model.attachments.get("files", []):
                fa = resolve_uri(fa, root_path=root_path)
                package[fa.name] = fa
                local_files.append(fa.name)

            if local_files:
                raw_model.attachments["files"] = local_files

        package["rdf.yaml"] = cls.serialize_raw_model(raw_model)
        return dict(package)

    @classmethod
    def get_matching_io_class(cls, data_version: str, action_descr: str):
        if not isinstance(data_version, str):
            raise TypeError("missing or invalid 'format_version'")

        data_version_wo_patch = cls.get_version_tuple_wo_patch(data_version)
        current_version_wo_patch = cls.get_current_format_version_wo_patch()
        if data_version_wo_patch > current_version_wo_patch:
            raise ValueError(
                f"You are attempting to {action_descr} an RDF in format version {'.'.join(map(str, data_version_wo_patch))}.x "
                f"with the RDF spec {'.'.join(map(str, current_version_wo_patch))}"
            )
        elif data_version_wo_patch == current_version_wo_patch:
            return cls
        elif cls.preceding_io_class is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            return cls.preceding_io_class

    @staticmethod
    def make_zip(path: pathlib.Path, content: Dict[str, Union[str, pathlib.Path]]):
        with ZipFile(path, "w") as myzip:
            for arc_name, file_or_str_content in content.items():
                if isinstance(file_or_str_content, str):
                    myzip.writestr(arc_name, file_or_str_content)
                else:
                    myzip.write(file_or_str_content, arcname=arc_name)

    @classmethod
    def ensure_raw_model(
        cls,
        raw_model: Union[str, dict, os.PathLike, raw_nodes.URI, RawModelNode],
        root_path: os.PathLike,
        update_to_current_format: bool,
    ):
        if isinstance(raw_model, cls.raw_nodes.Model):
            return raw_model, root_path

        if isinstance(raw_model, Node):
            # might be an older raw_model.Model
            # round trip to ensure correct raw model
            raw_model = cls.serialize_raw_model_to_dict(raw_model)
        elif isinstance(raw_model, dict):
            pass
        elif isinstance(raw_model, (str, os.PathLike, raw_nodes.URI)):
            raw_model = resolve_local_uri(raw_model, pathlib.Path())
            if isinstance(raw_model, pathlib.Path):
                root_path = raw_model.parent
        else:
            raise TypeError(raw_model)

        raw_model = cls.load_raw_model(raw_model, update_to_current_format)
        return raw_model, root_path

    @classmethod
    def maybe_convert_model(cls, data: dict):
        if cls.preceding_io_class is not None:
            data = cls.preceding_io_class.maybe_convert_model(data)

        return cls.converters.maybe_convert_model(data)

    @classmethod
    def _load_raw_model_from_dict_wo_format_conv(cls, data: dict):
        raw_model: cls.raw_nodes.Model = cls.schema.Model().load(data)
        assert isinstance(raw_model, cls.raw_nodes.Model)
        return raw_model

    @staticmethod
    def get_version_tuple_wo_patch(version: str):
        try:
            fvs = version.split(".")
            return int(fvs[0]), int(fvs[1])
        except Exception as e:
            raise ValidationError(f"invalid format_version '{version}' error: {e}")

    @classmethod
    def get_current_format_version_wo_patch(cls):
        return cls.get_version_tuple_wo_patch(get_args(cls.raw_nodes.ModelFormatVersion)[-1])
