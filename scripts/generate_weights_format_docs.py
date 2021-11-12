import dataclasses
import inspect
from pathlib import Path
from typing import List, Tuple, Type

import bioimageio.spec.model
from bioimageio.spec.model.v0_3.schema import WeightsEntry
from bioimageio.spec.shared.fields import DocumentedField

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


@dataclasses.dataclass
class Kwarg:
    name: str
    optional: bool
    description: str


@dataclasses.dataclass
class WeightsFormatDocNode:
    name: str
    description: str
    kwargs: List[Kwarg]


def get_doc(schema) -> List[WeightsFormatDocNode]:
    """retrieve documentation of weights formats from their definitions schema"""

    def get_kwargs_doc(we: Type[WeightsEntry]) -> List[Kwarg]:
        return sorted(
            [
                Kwarg(name=name, optional=not f.required or bool(f.missing), description=f.bioimageio_description)
                for name, f in we().fields.items()
                if name != "weights_format"
            ],
            key=lambda kw: (kw.optional, kw.name),
        )

    def get_wf_name_from_wf_schema(wfs):
        return wfs().fields["weights_format"].validate.comparable

    return [
        WeightsFormatDocNode(
            name=get_wf_name_from_wf_schema(wfs),
            description=wfs.bioimageio_description,
            kwargs=get_kwargs_doc(wfs),
        )
        for wfs in get_args(schema.WeightsEntry)  # schema.WeightsEntry is a typing.Union of weights format schemas
    ]


def markdown_from_doc(doc_nodes: List[WeightsFormatDocNode], title: str, description: str):
    md = f"# {title}\n{description}\n"

    for doc in doc_nodes:
        md += f"- `{doc.name}` {doc.description}\n"
        if doc.kwargs:
            md += f"  - key word arguments:\n"
            for kwarg in doc.kwargs:
                md += f"    - `{'[' if kwarg.optional else ''}{kwarg.name}{']' if kwarg.optional else ''}` {kwarg.description}\n"

    return md


def export_markdown_docs(folder: Path, spec) -> None:
    model_or_version = spec.__name__.split(".")[-1]
    format_version_wo_patch = ".".join(spec.format_version.split(".")[:2])
    if model_or_version == "model":
        format_version_file_name = "latest"
    else:
        format_version_file_name = format_version_wo_patch.replace(".", "_")

    doc = get_doc(spec.schema)
    assert isinstance(doc, list)
    md = markdown_from_doc(doc, title=f"Weights formats in model spec {format_version_wo_patch}", description="")
    path = folder / f"weights_formats_spec_{format_version_file_name}.md"
    path.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    import bioimageio.spec.model.v0_3

    dist = Path(__file__).parent / "../dist"
    dist.mkdir(exist_ok=True)

    export_markdown_docs(dist, bioimageio.spec.model.v0_3)
    export_markdown_docs(dist, bioimageio.spec.model)
