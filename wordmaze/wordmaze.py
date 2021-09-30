from __future__ import annotations

import copy

import enum
from functools import partial
from numbers import Real
from typing import Any, Callable, Iterable, Optional, Tuple, Type, TypeVar, Union, overload

from dataclassy import dataclass
from dataclassy.functions import replace

from wordmaze.utils.dataclasses import DataClassSequence, as_dict, as_tuple
from wordmaze.utils.sequences import MutableSequence

_T = TypeVar('_T')
_U = TypeVar('_U')


@dataclass(iter=True, kwargs=True)
class Box:
    x1: Real = None
    x2: Real = None
    y1: Real = None
    y2: Real = None

    def __post_init__(
        self, height: Optional[Real] = None, width: Optional[Real] = None
    ) -> None:
        if (self.x1, self.x2, width).count(None) != 1:
            raise ValueError(
                'exactly one of *x1*, *x2*, *width* must be *None* or omitted'
            )
        elif width is not None and width < 0:
            raise ValueError('*width* must be *None* (or omitted) or >=0')

        if (self.y1, self.y2, height).count(None) != 1:
            raise ValueError(
                'exactly one of *y1*, *y2*, *height* must be *None* (or omitted)'
            )
        elif height is not None and height < 0:
            raise ValueError('*height* must be *None* (or omitted) or >=0')

        if self.x1 is None:
            self.x1 = self.x2 - width
        elif self.x2 is None:
            self.x2 = self.x1 + width
        elif self.x1 > self.x2:
            self.x2, self.x1 = self.x1, self.x2

        if self.y1 is None:
            self.y1 = self.y2 - height
        elif self.y2 is None:
            self.y2 = self.y1 + height
        elif self.y1 > self.y2:
            self.y2, self.y1 = self.y1, self.y2

    @property
    def height(self) -> Real:
        return abs(self.y1 - self.y2)

    @property
    def width(self) -> Real:
        return abs(self.x1 - self.x2)

    @property
    def xmid(self) -> Real:
        return (self.x1 + self.x2) / 2

    @property
    def ymid(self) -> Real:
        return (self.y1 + self.y2) / 2


class Element(Box):
    pass


_Element = TypeVar('_Element', bound=Element)


class TextBox(Element):
    text: str
    confidence: Real


class FloatingElement(Element):
    caption: Optional[TextBox] = None


class Table(FloatingElement):
    pass


class Figure(FloatingElement):
    content: bytes
    image_type: str


class PageTextBox(TextBox):
    page: int


@dataclass(iter=True)
class Shape:
    height: Real
    width: Real


class Origin(enum.Enum):
    TOP_LEFT = enum.auto()
    BOTTOM_LEFT = enum.auto()


class Page(DataClassSequence[Element]):
    def __init__(
        self,
        shape: Shape,
        entries: Iterable[Element] = (),
        origin: Origin = Origin.TOP_LEFT,
    ) -> None:
        super().__init__(entries)
        self.shape: Shape = shape
        self.origin: Origin = origin

    def textboxes(self) -> DataClassSequence[TextBox]:
        return self.iter(TextBox)

    def figures(self) -> DataClassSequence[Figure]:
        return self.iter(Figure)

    def rebase(self, origin: Origin) -> Page:
        if origin is self.origin:
            return self
        elif (
            origin is Origin.BOTTOM_LEFT and self.origin is Origin.TOP_LEFT
        ) or (origin is Origin.TOP_LEFT and self.origin is Origin.BOTTOM_LEFT):

            def rebaser(element: _Element) -> _Element:
                return replace(
                    element,
                    y1=self.shape.height - element.y2,
                    y2=self.shape.height - element.y1,
                )

        else:
            raise NotImplementedError(
                'unsupported rebase operation:'
                f' from {self.origin} to {origin}.'
            )

        rebased = self.map(rebaser)
        rebased.origin = origin
        return rebased


class WordMaze(MutableSequence[Page]):
    def __init__(self, pages: Iterable[Page] = ()) -> None:
        super().__init__(pages)

    @property
    def shapes(self) -> Tuple[Shape, ...]:
        return tuple(page.shape for page in self)

    def textboxes(self) -> Iterable[PageTextBox]:
        return (
            PageTextBox(page=number, **as_dict(textbox))
            for number, page in enumerate(self)
            for textbox in page
        )

    def tuples(self) -> Iterable[tuple]:
        return map(partial(as_tuple, flatten=True), self.textboxes())

    def dicts(self) -> Iterable[dict]:
        return map(partial(as_dict, flatten=True), self.textboxes())

    def map(
        self,
        mapper: Optional[Callable[[Element], Element]] = None,
        /,
        **field_mappers: Callable[[Any], Any],
    ) -> WordMaze:
        return WordMaze(page.map(mapper, **field_mappers) for page in self)

    def filter(
        self,
        pred: Optional[Callable[[Element], bool]] = None,
        /,
        **field_preds: Callable[[Any], bool],
    ) -> WordMaze:
        return WordMaze(page.filter(pred, **field_preds) for page in self)
