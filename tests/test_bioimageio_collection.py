import datetime
import json
from pathlib import Path
from typing import Dict

import pooch  # type: ignore

from tests.unittest_utils import BaseTestCases


BASE_URL = "https://bioimage-io.github.io/collection-bioimage-io/"
RDF_BASE_URL = BASE_URL + "rdfs/"
WEEK = f"{datetime.datetime.now().year}week{datetime.datetime.now().isocalendar()[1]}"
CACHE_PATH = Path(__file__).parent / "cache" / WEEK


class TestBioimageioCollection(BaseTestCases.TestManyRdfs):
    rdf_root = CACHE_PATH / "rdfs"

    @classmethod
    def yield_rdf_paths(cls):
        with open(pooch.retrieve(BASE_URL + "collection.json", None), encoding="utf-8") as f:  # type: ignore
            collection_data = json.load(f)["collection"]

        collection_registry: Dict[str, None] = {
            entry["rdf_source"].replace(RDF_BASE_URL, ""): None for entry in collection_data
        }
        collection = pooch.create(  # type: ignore
            path=CACHE_PATH,
            base_url=RDF_BASE_URL,
            registry=collection_registry,
        )

        for rdf in collection_registry:
            yield Path(collection.fetch(rdf))  # type: ignore
