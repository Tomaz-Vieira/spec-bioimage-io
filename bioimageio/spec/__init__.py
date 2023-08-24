import json

from bioimageio.spec import application, collection, dataset, generic, model, notebook
from bioimageio.spec._internal.utils import files
from bioimageio.spec.application import AnyApplication, Application
from bioimageio.spec.collection import AnyCollection, Collection
from bioimageio.spec.dataset import AnyDataset, Dataset
from bioimageio.spec.description import (
    LatestResourceDescription,
    ResourceDescription,
    SpecificResourceDescription,
    load_description,
    validate_format,
)
from bioimageio.spec.generic import AnyGeneric, Generic
from bioimageio.spec.model import AnyModel, Model
from bioimageio.spec.notebook import AnyNotebook, Notebook

with files("bioimageio.spec").joinpath("VERSION").open("r", encoding="utf-8") as f:
    __version__: str = json.load(f)["version"]
    assert isinstance(__version__, str)

from typing_extensions import TypeAliasType

__all__ = (
    "__version__",
    "AnyApplication",
    "AnyCollection",
    "AnyDataset",
    "AnyGeneric",
    "AnyModel",
    "AnyNotebook",
    "application",
    "Application",
    "collection",
    "Collection",
    "dataset",
    "Dataset",
    "generic",
    "Generic",
    "LatestResourceDescription",
    "load_description",
    "model",
    "Model",
    "notebook",
    "Notebook",
    "ResourceDescription",
    "SpecificResourceDescription",
    "validate_format",
)
