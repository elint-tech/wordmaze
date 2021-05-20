import enum
from numbers import Real
from typing import Any, Callable, Iterable, List, Optional, Tuple

from dataclassy import dataclass
from dataclassy.dataclass import Internal
from dataclassy.functions import replace

from wordmaze.utils.dataclasses import DataClassSequence
from wordmaze.utils.sequences import MutableSequence


@dataclass(iter=True, kwargs=True)
class Box:
    x1: Real = None
    x2: Real = None
    y1: Real = None
    y2: Real = None

    def __post_init__(
            self,
            height: Optional[Real] = None,
            width: Optional[Real] = None
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
        else:
            if self.x1 > self.x2:
                self.x2, self.x1 = self.x1, self.x2
            width = self.x2 - self.x1

        if self.y1 is None:
            self.y1 = self.y2 - height
        elif self.y2 is None:
            self.y2 = self.y1 + height
        else:
            if self.y1 > self.y2:
                self.y2, self.y1 = self.y1, self.y2
            height = self.y2 - self.y1

        self._height: Real = height
        self._width: Real = width

    @property
    def height(self) -> Real:
        return self._height

    @property
    def width(self) -> Real:
        return self._width


class TextBox(Box):
    text: str
    confidence: Real


@dataclass(iter=True)
class Shape:
    height: Real
    width: Real


class Origin(enum.Enum):
    TOP_LEFT = enum.auto()
    BOTTOM_LEFT = enum.auto()


class Page(DataClassSequence[TextBox]):
    def __init__(
            self,
            shape: Shape,
            entries: Iterable[TextBox] = (),
            origin: Origin = Origin.TOP_LEFT
    ) -> None:
        super().__init__(entries)
        self.shape: Shape = shape
        self.origin: Origin = origin

    def map(
            self,
            *mapper: Callable[[TextBox], TextBox],
            **field_mappers: Callable[[Any], Any]
    ) -> 'Page':
        return Page(
            shape=self.shape,
            origin=self.origin,
            entries=super().map(*mapper, **field_mappers)
        )

    def filter(
            self,
            *pred: Callable[[TextBox], bool],
            **field_preds: Callable[[Any], bool]
    ) -> 'Page':
        return Page(
            shape=self.shape,
            origin=self.origin,
            entries=super().filter(*pred, **field_preds)
        )

    def rebase(self, origin: Origin) -> 'Page':
        if origin is self.origin:
            return self
        elif (
            (origin is Origin.BOTTOM_LEFT and self.origin is Origin.TOP_LEFT)
            or (origin is Origin.TOP_LEFT and self.origin is Origin.BOTTOM_LEFT)
        ):
            def rebaser(textbox: TextBox) -> TextBox:
                return replace(
                    textbox,
                    y1=self.shape.height - textbox.y2,
                    y2=self.shape.height - textbox.y1
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

    def tuples(self) -> Iterable[tuple]:
        return (
            (number,) + tpl
            for number, page in enumerate(self)
            for tpl in page.tuples()
        )

    def dicts(self) -> Iterable[dict]:
        return (
            dict(dct, page=number)
            for number, page in enumerate(self)
            for dct in page.dicts()
        )

    def map(
            self,
            *mapper: Callable[[TextBox], TextBox],
            **field_mappers: Callable[[Any], Any]
    ) -> 'WordMaze':
        return WordMaze(page.map(*mapper, **field_mappers) for page in self)

    def filter(
            self,
            *pred: Callable[[TextBox], bool],
            **field_preds: Callable[[Any], bool]
    ) -> 'WordMaze':
        return WordMaze(page.filter(*pred, **field_preds) for page in self)
