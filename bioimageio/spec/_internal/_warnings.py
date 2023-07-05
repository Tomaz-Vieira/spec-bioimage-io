import dataclasses
import sys
from logging import getLogger
from types import MappingProxyType
from typing import (
    Any,
    Dict,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
)

from annotated_types import BaseMetadata, GroupedMetadata
from pydantic import FieldValidationInfo, TypeAdapter, ValidationInfo
from pydantic._internal._decorators import inspect_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import (
    GeneralValidatorFunction,
    NoInfoValidatorFunction,
)
from typing_extensions import Annotated, LiteralString

WARNINGS_ACTION_KEY = "warnings_action"
RAISE_WARNINGS = "raise"

ALERT = 35  # no ALERT or worse -> RDF is worriless
WARNING = 30  # no WARNING or worse -> RDF is watertight
INFO = 20
Severity = Literal[20, 30, 35]

if sys.version_info < (3, 10):
    SLOTS: Dict[str, Any] = {}
else:
    SLOTS = {"slots": True}


ValidatorFunction = Union[NoInfoValidatorFunction, GeneralValidatorFunction]

AnnotationMetaData = Union[BaseMetadata, GroupedMetadata]

WarningType = Literal["info", "worriless", "watertight"]
SEVERITY_TO_TYPE: MappingProxyType[Severity, WarningType] = MappingProxyType(
    {INFO: "info", WARNING: "worriless", ALERT: "watertight"}
)


def raise_warning(message_template: LiteralString, *, severity: Severity, context: Optional[Dict[str, Any]]):
    raise PydanticCustomError(SEVERITY_TO_TYPE[severity], message_template, context)


def warn(
    typ: Union[AnnotationMetaData, Any],
    severity: Severity = 20,
    msg: Optional[LiteralString] = None,
):
    """treat a type or its annotation metadata as a warning condition"""
    assert get_origin(AnnotationMetaData) is Union
    if isinstance(typ, get_args(AnnotationMetaData)):
        typ = Annotated[Any, typ]

    validator = TypeAdapter(typ)
    return BeforeWarner(validator.validate_python, severity=severity, msg=msg)


def call_validator_func(
    func: GeneralValidatorFunction, mode: Literal["after", "before", "plain", "wrap"], value: Any, info: ValidationInfo
) -> Any:
    info_arg = inspect_validator(func, mode)
    if info_arg:
        return func(value, info)  # type: ignore
    else:
        return func(value)  # type: ignore


def as_warning(
    func: GeneralValidatorFunction,
    *,
    mode: Literal["after", "before", "plain", "wrap"] = "after",
    severity: Severity = 20,
    msg: Optional[LiteralString] = None,
) -> GeneralValidatorFunction:
    """turn validation function into a no-op, but may raise if `context["warnings"] == "raise"`"""

    def wrapper(value: Any, info: Union[FieldValidationInfo, ValidationInfo]) -> Any:
        logger = getLogger(getattr(info, "field_name", "node"))
        if logger.level > severity:
            return value

        try:
            call_validator_func(func, mode, value, info)
        except (AssertionError, ValueError) as e:
            logger.log(severity, e)
            if info.context is not None and info.context.get(WARNINGS_ACTION_KEY) == RAISE_WARNINGS:
                raise_warning(msg or ",".join(e.args), severity=severity, context=dict(value=value))

        return value

    return wrapper


@dataclasses.dataclass(frozen=True, **SLOTS)
class _WarnerMixin:
    severity: Severity = 20
    msg: Optional[LiteralString] = None

    def __getattribute__(self, __name: str) -> Any:
        ret = super().__getattribute__(__name)
        if __name == "func":
            return as_warning(ret, severity=self.severity, msg=self.msg)
        else:
            return ret


@dataclasses.dataclass(frozen=True, **SLOTS)
class AfterWarner(_WarnerMixin, AfterValidator):
    """Like AfterValidator, but wraps validation `func` with the `warn` decorator"""


@dataclasses.dataclass(frozen=True, **SLOTS)
class BeforeWarner(_WarnerMixin, BeforeValidator):
    """Like BeforeValidator, but wraps validation `func` with the `warn` decorator"""
