import enum
from functools import partial
from numbers import Real
from typing import Iterable, List, MutableSequence, Tuple

from dataclassy import dataclass
from dataclassy.functions import replace

from wordmaze.utils.dataclasses import as_dict, as_tuple


@dataclass(iter=True, kwargs=True)
class Box:
    x1: Real
    x2: Real
    y1: Real
    y2: Real


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


class Page(MutableSequence[TextBox]):
    def __init__(
            self,
            shape: Shape,
            entries: Iterable[TextBox] = (),
            origin: Origin = Origin.TOP_LEFT
    ) -> None:
        self.shape: Shape = shape
        self._entries: List[TextBox] = list(entries)
        self.origin = origin

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._entries})'

    def __getitem__(self, index: int) -> TextBox:
        return self._entries[index]

    def __setitem__(self, index: int, entry: TextBox) -> None:
        self._entries[index] = entry

    def __delitem__(self, index: int) -> None:
        del self._entries[index]

    def __len__(self) -> int:
        return len(self._entries)

    def insert(self, index: int, entry: TextBox) -> None:
        self._entries.insert(index, entry)

    def tuples(self) -> Iterable[tuple]:
        return map(
            partial(as_tuple, flatten=True),
            self
        )

    def dicts(self) -> Iterable[dict]:
        return map(
            partial(as_dict, flatten=True),
            self
        )

    def rebased(self, origin: Origin) -> 'Page':
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

        return Page(
            shape=self.shape,
            origin=origin,
            entries=map(rebaser, self)
        )


class WordMaze(MutableSequence[Page]):
    def __init__(self, pages: Iterable[Page] = ()) -> None:
        self._pages: List[Page] = list(pages)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._pages})'

    def __getitem__(self, index: int) -> Page:
        return self._pages[index]

    def __setitem__(self, index: int, page: Page) -> None:
        self._pages[index] = page

    def __delitem__(self, index: int) -> None:
        del self._pages[index]

    def __len__(self) -> int:
        return len(self._pages)

    def insert(self, index: int, page: Page) -> None:
        self._pages.insert(index, page)

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
