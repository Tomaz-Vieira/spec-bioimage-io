from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Type
from unittest import TestCase

from pydantic import ValidationError

from bioimageio.spec.shared.nodes import Node


@dataclass
class SubTest(ABC):
    kwargs: Dict[str, Any]
    name: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    node_class: Optional[Type[Node]] = None

    def __post_init__(self):
        if self.__class__ == SubTest:
            raise TypeError("Cannot instantiate abstract class.")


@dataclass
class Valid(SubTest):
    expected_dump_raw: Optional[Dict[str, Any]] = None
    expected_dump_python: Optional[Dict[str, Any]] = None


@dataclass
class Invalid(SubTest):
    expect: Type[Exception] = ValidationError


class BaseTestCases:
    """class to hide base test cases to not discover them as tests"""

    class TestNode(TestCase):
        """template to test any Node subclass with valid and invalid kwargs"""

        default_node_class: Type[Node]
        default_context: Dict[str, Any] = dict(root=Path(__file__).parent)

        sub_tests: Sequence[SubTest]

        def test_valid(self):
            for st in self.sub_tests:
                if isinstance(st, Invalid):
                    continue

                assert isinstance(st, Valid)
                with self.subTest(**self.get_subtest_kwargs(st)):
                    nc = self.get_node_class(st)
                    node = nc.model_validate(st.kwargs, context=self.get_context(st))
                    for mode, expected in [
                        ("python", st.expected_dump_python),
                        ("json", st.expected_dump_raw),
                    ]:
                        with self.subTest(_dump_mode=mode):
                            actual = node.model_dump(mode=mode, round_trip=True)
                            assert expected is None or actual == expected, (actual, expected)

        def test_invalid(self):
            for st in self.sub_tests:
                if isinstance(st, Valid):
                    continue

                assert isinstance(st, Invalid)
                with self.subTest(**self.get_subtest_kwargs(st)):
                    nc = self.get_node_class(st)
                    self.assertRaises(st.expect, nc.model_validate, st.kwargs, context=self.get_context(st))

        def get_context(self, st: SubTest) -> Dict[str, Any]:
            if st.context is None:
                return self.default_context
            else:
                return st.context

        def get_node_class(self, st: SubTest) -> Type[Node]:
            return st.node_class or self.default_node_class

        @staticmethod
        def get_subtest_kwargs(st: SubTest) -> Dict[str, Any]:
            if st.name is not None:
                return dict(name=st.name)
            else:
                ret = dict(st.kwargs)
                if st.context is not None:
                    ret["context"] = st.context

                return ret