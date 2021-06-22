from pathlib import Path

from bioimageio.spec.shared.nodes import ImportedSource
from .raw_nodes import *


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing


@dataclass
class WeightsEntry(WeightsEntry):
    source: Path = missing


@dataclass
class Model(Model):
    source: ImportedSource = missing
    test_inputs: List[Path] = missing
    test_outputs: List[Path] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing