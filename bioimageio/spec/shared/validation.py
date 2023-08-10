from __future__ import annotations

import pathlib
from contextvars import ContextVar, Token
from types import MappingProxyType
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

import pydantic
from pydantic import AnyUrl, DirectoryPath, PrivateAttr
from pydantic_core.core_schema import ErrorType
from typing_extensions import NotRequired, TypedDict

Severity = Literal[20, 30, 35]
WarningLevel = Literal[Severity, 50]  # with warning level x raise warnings of severity >=x
ALERT = 35  # no ALERT -> RDF is worriless
WARNING = 30  # no ALERT nor WARNING -> RDF is watertight
INFO = 20

WarningType = Literal["info", "warning", "alert"]
SEVERITY_TO_WARNING: MappingProxyType[Severity, WarningType] = MappingProxyType(
    {INFO: "info", WARNING: "warning", ALERT: "alert"}
)


class ValidationContext(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", validate_assignment=True)
    root: Union[DirectoryPath, AnyUrl] = pathlib.Path()
    """url/path serving as base to any relative file paths. Default provided as data field `root`.0"""

    warning_level: WarningLevel = 50
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    original_format: Optional[Tuple[int, int, int]] = None
    """original format version of the validation data (set dynamically when validating resource descriptions)."""

    collection_base_content: Optional[Dict[str, Any]] = None
    """Collection base content (set dynamically during validation of collection resource descriptions)."""

    _token: Token[ValidationContext] = PrivateAttr()

    def __enter__(self):
        self._token = validation_context_var.set(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):  # type: ignore
        validation_context_var.reset(self._token)


validation_context_var = ContextVar("_validation_context_var", default=ValidationContext())


class ValidationOutcome(TypedDict):
    loc: Tuple[Union[int, str], ...]
    msg: str


class ValidationError(ValidationOutcome):
    type: Union[ErrorType, str]


class ValidationWarning(ValidationOutcome):
    type: WarningType


class ValidationSummary(TypedDict):
    bioimageio_spec_version: str
    name: str
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    errors: Sequence[ValidationError]
    traceback: NotRequired[Sequence[str]]
    warnings: Sequence[ValidationWarning]


class LegacyValidationSummary(TypedDict):
    bioimageio_spec_version: str
    error: Union[None, str, Dict[str, Any]]
    name: str
    nested_errors: NotRequired[Dict[str, Dict[str, Any]]]
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    traceback: Optional[List[str]]
    warnings: Dict[str, Any]
