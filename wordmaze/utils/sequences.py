from typing import Iterable, List
from typing import MutableSequence as BaseSequence
from typing import TypeVar

_Entry = TypeVar('_Entry')


class MutableSequence(BaseSequence[_Entry]):
    def __init__(self, entries: Iterable[_Entry] = ()) -> None:
        self.__entries__: List[_Entry] = list(entries)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self.__entries__})'

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, index: int) -> _Entry:
        return self.__entries__[index]

    def __setitem__(self, index: int, entry: _Entry) -> None:
        self.__entries__[index] = entry

    def __delitem__(self, index: int) -> None:
        del self.__entries__[index]

    def __len__(self) -> int:
        return len(self.__entries__)

    def insert(self, index: int, entry: _Entry) -> None:
        self.__entries__.insert(index, entry)
