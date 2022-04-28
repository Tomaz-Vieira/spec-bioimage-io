import dataclasses
import os
import pathlib
import typing

from marshmallow import missing
from marshmallow.utils import _Missing

from . import raw_nodes
from ._resolve_source import resolve_local_source, resolve_source as _resolve_source

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore

GenericResolvedNode = typing.TypeVar("GenericResolvedNode", bound=raw_nodes.RawNode)
GenericRawNode = typing.TypeVar("GenericRawNode", bound=raw_nodes.RawNode)
GenericRawRD = typing.TypeVar("GenericRawRD", bound=raw_nodes.ResourceDescription)
URI_Type = typing.TypeVar("URI_Type", bound=raw_nodes.URI)


def iter_fields(node: GenericRawNode):
    for field in dataclasses.fields(node):
        yield field.name, getattr(node, field.name)


class NodeVisitor:
    def visit(self, node: typing.Any) -> None:
        method = "visit_" + node.__class__.__name__

        visitor: typing.Callable[[typing.Any], typing.Any] = getattr(self, method, self.generic_visit)

        visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""

        if isinstance(node, raw_nodes.RawNode):
            for field, value in iter_fields(node):
                self.visit(value)
        elif isinstance(node, dict):
            [self.visit(subnode) for subnode in node.values()]
        elif isinstance(node, (tuple, list)):
            [self.visit(subnode) for subnode in node]


class Transformer:
    def transform(self, node: typing.Any, **kwargs) -> typing.Any:
        method = "transform_" + node.__class__.__name__

        transformer = getattr(self, method, self.generic_transformer)

        return transformer(node, **kwargs)  # noqa

    def generic_transformer(self, node: typing.Any, **kwargs) -> typing.Any:
        return node

    def transform_list(self, node: list, **kwargs) -> list:
        return [self.transform(subnode, **kwargs) for subnode in node]

    def transform_dict(self, node: dict, **kwargs) -> dict:
        return {key: self.transform(value, **kwargs) for key, value in node.items()}


class NestedUpdateTransformer:
    """update a nested dict/list/raw_node with a nested dict/list update"""

    DROP = "DROP"
    KEEP = "KEEP"

    def transform(self, node: typing.Any, update: typing.Any) -> typing.Any:
        if update == self.KEEP:
            return node

        if isinstance(update, raw_nodes.RawNode):
            raise TypeError("updating with raw node is not allowed")

        method = "transform_" + node.__class__.__name__
        transformer = getattr(self, method, self.generic_transformer)

        return transformer(node, update)  # noqa

    def generic_transformer(self, node: typing.Any, update: typing.Any) -> typing.Any:
        if isinstance(node, raw_nodes.RawNode):
            return self.transform_node(node, update)
        else:
            return update

    def transform_node(
        self, node: raw_nodes.RawNode, update: typing.Union[dict, typing.Any]
    ) -> typing.Union[raw_nodes.RawNode, typing.Any]:
        if isinstance(update, dict):
            updated_kwargs = {
                name: self.transform(value, update.get(name, self.KEEP)) for name, value in iter_fields(node)
            }

            if "format_version" in update:
                # add new fields
                for k in set(update) - set(updated_kwargs):
                    updated_kwargs[k] = update[k]

                # todo: resolve raw node for updated format_version
                raise NotImplementedError("Updating format_version not yet implemented")
            else:
                invalid_updates = set(update) - set(updated_kwargs)
                if invalid_updates:
                    raise ValueError(f"Got unexpected updates for non-existing fields: {invalid_updates}")

            return dataclasses.replace(node, **updated_kwargs)
        else:
            return update

    def transform_list(self, node: list, update: typing.Union[list, typing.Any]) -> typing.Union[list, typing.Any]:
        if isinstance(update, list):
            if len(update) < len(node):
                update = update + [self.KEEP] * (len(node) - len(update))

            if len(node) < len(update):
                node = node + [self.DROP] * (len(update) - len(node))

            node = [self.transform(n, u) for n, u in zip(node, update)]
            return [e for e in node if e != self.DROP]
        else:
            return update

    def transform_dict(self, node: dict, update: typing.Union[dict, typing.Any]) -> typing.Union[dict, typing.Any]:
        if isinstance(update, dict):
            ret = {k: self.transform(v, update.get(k, self.KEEP)) for k, v in node.items()}
            for k, v in update.items():
                if k not in ret:
                    ret[k] = v

            return {k: v for k, v in ret.items() if v != self.DROP}
        else:
            return update


class NodeTransformer(Transformer):
    def generic_transformer(self, node: GenericRawNode, **kwargs) -> GenericRawNode:
        if isinstance(node, raw_nodes.RawNode):
            return dataclasses.replace(
                node, **{name: self.transform(value, **kwargs) for name, value in iter_fields(node)}
            )
        else:
            return super().generic_transformer(node, **kwargs)


class NodeTransformerKnownParent(NodeTransformer):
    def generic_transformer(
        self,
        node: GenericRawNode,
        name: typing.Optional[str] = None,
        parent: typing.Optional[raw_nodes.RawNode] = None,
        **kwargs,
    ) -> GenericRawNode:
        if isinstance(node, raw_nodes.RawNode):
            return dataclasses.replace(
                node, **{n: self.transform(value, name=n, parent=node) for n, value in iter_fields(node)}
            )
        else:
            return super().generic_transformer(node, name=name, parent=parent)


class PathToRemoteUriTransformer(NodeTransformer):
    def __init__(self, *, remote_source: URI_Type):
        remote_path = pathlib.PurePosixPath(remote_source.path).parent.as_posix()
        self.remote_root = dataclasses.replace(remote_source, path=remote_path, uri_string=None)

    def transform_URI(self, node: URI_Type) -> URI_Type:
        if node.scheme == "file":
            assert not node.authority
            assert not node.query
            assert not node.fragment
            return self._transform_Path(pathlib.Path(node.path))

        return node

    def _transform_Path(self, leaf: pathlib.PurePath):
        assert not leaf.is_absolute()
        path = pathlib.PurePosixPath(self.remote_root.path) / leaf
        return dataclasses.replace(self.remote_root, path=path.as_posix(), uri_string=None)

    def transform_PurePath(self, leaf: pathlib.PurePath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PurePosixPath(self, leaf: pathlib.PurePosixPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PureWindowsPath(self, leaf: pathlib.PureWindowsPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_PosixPath(self, leaf: pathlib.PosixPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath) -> raw_nodes.URI:
        return self._transform_Path(leaf)


class RawNodePackageTransformer(NodeTransformer):
    """Transforms raw node fields specified by <node>._include_in_package to local relative paths.
    Adds remote resources to given dictionary."""

    def __init__(
        self, remote_resources: typing.Dict[str, typing.Union[pathlib.PurePath, raw_nodes.URI]], root: pathlib.Path
    ):
        super().__init__()
        self.remote_resources = remote_resources
        self.root = root

    def _transform_resource(
        self, resource: typing.Union[list, pathlib.PurePath, raw_nodes.URI]
    ) -> typing.Union[typing.List[pathlib.Path], _Missing, pathlib.Path]:
        if isinstance(resource, list):
            return [self._transform_resource(r) for r in resource]  # type: ignore  # todo: improve annotation
        elif resource is missing:
            return resource
        elif isinstance(resource, pathlib.PurePath):
            name_from = resource
            if resource.is_absolute():
                folder_in_package = ""
            else:
                if resource.parent.as_posix() == ".":
                    folder_in_package = ""
                else:
                    folder_in_package = resource.parent.as_posix() + "/"

                resource = self.root / resource

        elif isinstance(resource, raw_nodes.URI):
            name_from = pathlib.PurePath(resource.path or "unknown")
            folder_in_package = ""
        else:
            raise TypeError(f"Unexpected type {type(resource)} for {resource}")

        stem = name_from.stem
        suffix = name_from.suffix

        conflict_free_name = f"{folder_in_package}{stem}{suffix}"
        for i in range(100000):
            existing_resource = self.remote_resources.get(conflict_free_name)
            if existing_resource is not None and existing_resource != resource:
                conflict_free_name = f"{folder_in_package}{stem}-{i}{suffix}"
            else:
                break
        else:
            raise ValueError(f"Attempting to pack too many resources with name {stem}{suffix}")

        self.remote_resources[conflict_free_name] = resource

        return pathlib.Path(conflict_free_name)

    def generic_transformer(self, node: GenericRawNode, **kwargs) -> GenericRawNode:
        if isinstance(node, raw_nodes.RawNode):
            resolved_data = {
                field.name: self.transform(getattr(node, field.name), **kwargs) for field in dataclasses.fields(node)
            }
            for incl_field in node._include_in_package:
                field_value = resolved_data[incl_field]
                if field_value is not missing:  # optional fields might be missing
                    resolved_data[incl_field] = self._transform_resource(field_value)

            return dataclasses.replace(node, **resolved_data)
        else:
            return super().generic_transformer(node, **kwargs)


class AbsoluteToRelativePathTransformer(NodeTransformer):
    def __init__(self, *, root_path: os.PathLike):
        self.root_path = pathlib.Path(root_path).resolve()

    def transform_ImportableSourceFile(
        self, node: raw_nodes.ImportableSourceFile, **kwargs
    ) -> raw_nodes.ImportableSourceFile:
        assert isinstance(node.source_file, pathlib.Path)
        sf = node.source_file.relative_to(self.root_path) if node.source_file.is_absolute() else node.source_file
        return raw_nodes.ImportableSourceFile(source_file=sf, callable_name=node.callable_name)

    def _transform_Path(self, leaf: pathlib.Path):
        if leaf.is_absolute():
            return leaf.relative_to(self.root_path)
        else:
            return leaf

    def transform_PosixPath(self, leaf: pathlib.PosixPath, **kwargs) -> pathlib.Path:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath, **kwargs) -> pathlib.Path:
        return self._transform_Path(leaf)


class RelativeToAbsolutePathTransformer(NodeTransformer):
    def __init__(self, *, root_path: os.PathLike):
        self.root_path = pathlib.Path(root_path).resolve()

    def transform_ImportableSourceFile(
        self, node: raw_nodes.ImportableSourceFile, **kwargs
    ) -> raw_nodes.ImportableSourceFile:
        return raw_nodes.ImportableSourceFile(
            source_file=resolve_local_source(node.source_file, self.root_path), callable_name=node.callable_name
        )

    def _transform_Path(self, leaf: pathlib.Path):
        return self.root_path / leaf

    def transform_PosixPath(self, leaf: pathlib.PosixPath, **kwargs) -> pathlib.Path:
        return self._transform_Path(leaf)

    def transform_WindowsPath(self, leaf: pathlib.WindowsPath, **kwargs) -> pathlib.Path:
        return self._transform_Path(leaf)


class UriNodeTransformer(NodeTransformerKnownParent, RelativeToAbsolutePathTransformer):
    def __init__(self, *, root_path: os.PathLike, uri_only_if_in_package: bool = False):
        super().__init__(root_path=root_path)
        self.uri_only_if_in_package = uri_only_if_in_package

    def transform_URI(
        self, node: raw_nodes.URI, name: typing.Optional[str] = None, parent: typing.Optional[raw_nodes.RawNode] = None
    ) -> typing.Union[raw_nodes.URI, pathlib.Path]:
        if self.uri_only_if_in_package and ((name is None or parent is None) or name not in parent._include_in_package):
            return node
        else:
            local_path = _resolve_source(node, root_path=self.root_path)
            return local_path

    def transform_ImportableSourceFile(
        self, node: raw_nodes.ImportableSourceFile, **kwargs
    ) -> raw_nodes.ResolvedImportableSourceFile:
        return raw_nodes.ResolvedImportableSourceFile(
            source_file=_resolve_source(node.source_file, self.root_path), callable_name=node.callable_name
        )

    def transform_ImportableModule(self, node: raw_nodes.ImportableModule, **kwargs) -> raw_nodes.LocalImportableModule:
        return raw_nodes.LocalImportableModule(**dataclasses.asdict(node), root_path=self.root_path)