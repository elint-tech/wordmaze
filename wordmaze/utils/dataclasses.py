from __future__ import annotations

import copy
import textwrap
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

import funcy
from dataclassy import DataClass, asdict, astuple, values
from dataclassy.functions import is_dataclass_instance, replace

from wordmaze.utils.sequences import MutableSequence
from wordmaze.utils.typing import isa

_DataClass = TypeVar('_DataClass', bound=DataClass)
_T = TypeVar('_T')
_U = TypeVar('_U')


def as_dict(obj: DataClass, *, flatten: bool = False) -> Dict[str, Any]:
    if flatten:
        return funcy.join(
            (
                as_dict(field, flatten=flatten)
                if is_dataclass_instance(field)
                else {field_name: field}
            )
            for field_name, field in values(obj).items()
        )
    else:
        return asdict(obj)


def as_tuple(obj: DataClass, *, flatten: bool = False) -> Tuple[Any, ...]:
    if flatten:
        return funcy.join(
            (
                as_tuple(field, flatten=flatten)
                if is_dataclass_instance(field)
                else (field,)
            )
            for field in values(obj).values()
        )
    else:
        return astuple(obj)


class DataClassEntryMapper(Generic[_DataClass]):
    def __init__(self, mapper: Callable[[_DataClass], _DataClass], /) -> None:
        self._mapper: Callable[[_DataClass], _DataClass] = mapper

    def __call__(self, obj: _DataClass, /) -> _DataClass:
        return self._mapper(obj)

    @classmethod
    def restricted(
        cls,
        type_: Type[_T],
        mapper: Callable[[_T], _DataClass],
        /,
    ) -> DataClassEntryMapper[_DataClass]:
        def _mapper(obj: _DataClass, /) -> _DataClass:
            if isinstance(obj, type_):
                return mapper(obj)
            else:
                return obj

        return DataClassEntryMapper(_mapper)

    @classmethod
    def from_field_mappers(
        cls, **field_mappers: Callable[[_T], _T]
    ) -> DataClassEntryMapper[_DataClass]:
        def _mapper(obj: _DataClass, /) -> _DataClass:
            obj_dict = as_dict(obj)

            if keys_diff := frozenset(field_mappers).difference(obj_dict):
                raise TypeError(
                    f'fields {sorted(keys_diff)} do not exist in object'
                    f' {obj} from the class {type(obj)}.'
                )

            changes = {
                field_name: field_mapper(value)
                for field_name, (field_mapper, value) in funcy.zip_dicts(
                    field_mappers, obj_dict
                )
            }

            return replace(obj, **changes)

        return DataClassEntryMapper(_mapper)


class DataClassEntryFilter(Generic[_DataClass]):
    def __init__(self, pred: Callable[[_DataClass], bool], /) -> None:
        self._pred: Callable[[_DataClass], bool] = pred

    def __call__(self, obj: _DataClass, /) -> bool:
        return self._pred(obj)

    @classmethod
    def restricted(
        cls, type_: Type[_T], pred: Callable[[_T], bool], /
    ) -> DataClassEntryFilter[_DataClass]:
        def _pred(obj: _DataClass, /) -> bool:
            return not isinstance(obj, type_) or pred(obj)

        return DataClassEntryFilter(_pred)

    @classmethod
    def from_field_preds(
        cls, **field_preds: Callable[[_T], bool]
    ) -> DataClassEntryFilter[_DataClass]:
        def _pred(obj: _DataClass, /) -> bool:
            obj_dict = as_dict(obj)

            if keys_diff := frozenset(field_preds).difference(obj_dict):
                raise TypeError(
                    f'fields {sorted(keys_diff)} do not exist in object'
                    f' {obj} from the class {type(obj)}.'
                )

            obj_dict = funcy.project(obj_dict, field_preds)
            preds = (
                _field_pred(obj_dict[field_name])
                for field_name, _field_pred in field_preds.items()
            )

            return all(preds)

        return DataClassEntryFilter(_pred)


@overload
def field_mapper(
    mapper: Callable[[_DataClass], _DataClass], /
) -> Callable[[_DataClass], _DataClass]:
    ...


@overload
def field_mapper(
    type_: Type[_T], mapper: Callable[[_T], _DataClass], /
) -> Callable[[_DataClass], _DataClass]:
    ...


@overload
def field_mapper(
    **field_mappers: Callable[[_T], _T]
) -> Callable[[_DataClass], _DataClass]:
    ...


@overload
def field_mapper(
    type_: Type[_U], /, **field_mappers: Callable[[_T], _T]
) -> Callable[[_DataClass], _DataClass]:
    ...


def field_mapper(
    type_or_mapper: Optional[
        Union[Callable[[_DataClass], _DataClass], Type[_U]]
    ] = None,
    mapper: Optional[Callable[[_U], _DataClass]] = None,
    /,
    **field_mappers: Callable[[_T], _T],
) -> Callable[[_DataClass], _DataClass]:
    if isinstance(type_or_mapper, type):
        if mapper is not None and not field_mappers:
            return DataClassEntryMapper.restricted(type_or_mapper, mapper)
        elif mapper is None and field_mappers:
            return DataClassEntryMapper.restricted(
                type_or_mapper, field_mapper(**field_mappers)
            )
    elif callable(type_or_mapper) and mapper is None and not field_mappers:
        return DataClassEntryMapper(type_or_mapper)
    elif type_or_mapper is None and mapper is None and field_mappers:
        return DataClassEntryMapper.from_field_mappers(**field_mappers)

    raise TypeError(
        textwrap.dedent(
            '*field_mapper* accepts either a mapper or keyworded mappers, '
            'optionally prepended by a type. '
            '''
            For instance:
                - field_mapper(lambda textbox: process_textbox(textbox))
                - field_mapper(
                        TextBox,
                        lambda textbox: process_textbox(textbox)
                    )
                - field_mapper(
                        x1=lambda x1: x1 + 5,
                        x2=lambda x2: x2**2,
                        text=lambda text: text.upper()
                    )
                - field_mapper(
                        TextBox,
                        x1=lambda x1: x1 + 5,
                        x2=lambda x2: x2**2,
                        text=lambda text: text.upper()
                    )
            '''
        )
    )


@overload
def field_pred(
    pred: Callable[[_DataClass], bool], /
) -> Callable[[_DataClass], bool]:
    ...


@overload
def field_pred(
    type_: Type[_T], pred: Callable[[_T], bool], /
) -> Callable[[_DataClass], bool]:
    ...


@overload
def field_pred(
    **field_preds: Callable[[_T], bool]
) -> Callable[[_DataClass], bool]:
    ...


@overload
def field_pred(
    type_: Type[_U], /, **field_preds: Callable[[_T], bool]
) -> Callable[[_DataClass], bool]:
    ...


def field_pred(
    type_or_pred: Optional[
        Union[Callable[[_DataClass], bool], Type[_U]]
    ] = None,
    pred: Optional[Callable[[_DataClass], bool]] = None,
    /,
    **field_preds: Callable[[_T], bool],
) -> Callable[[_DataClass], bool]:
    if isinstance(type_or_pred, type):
        if pred is not None and not field_preds:
            return DataClassEntryFilter.restricted(type_or_pred, pred)
        elif pred is None and field_preds:
            return DataClassEntryFilter.restricted(
                type_or_pred, field_pred(**field_preds)
            )
    elif callable(type_or_pred) and pred is None and not field_preds:
        return DataClassEntryFilter(type_or_pred)
    elif type_or_pred is None and pred is None and field_preds:
        return DataClassEntryFilter.from_field_preds(**field_preds)

    raise TypeError(
        textwrap.dedent(
            '*field_pred* accepts either a pred or keyworded preds, '
            'optionally prepended by a type. '
            '''
            For instance:
                - field_pred(lambda textbox: process_textbox(textbox))
                - field_pred(
                        TextBox,
                        lambda textbox: process_textbox(textbox)
                    )
                - field_pred(
                        x1=lambda x1: x1 + 5,
                        x2=lambda x2: x2**2,
                        text=lambda text: text.upper()
                    )
                - field_pred(
                        TextBox,
                        x1=lambda x1: x1 + 5,
                        x2=lambda x2: x2**2,
                        text=lambda text: text.upper()
                    )
            '''
        )
    )


class DataClassSequence(MutableSequence[_DataClass]):
    def __init__(self, entries: Iterable[_DataClass] = ()) -> None:
        super().__init__(entries)

    def iter(self, type_: Type[_T], /) -> DataClassSequence[_DataClass]:
        return DataClassSequence(filter(isa(type_), self))

    def tuples(self) -> Iterable[Tuple[Any, ...]]:
        return map(partial(as_tuple, flatten=True), self)

    def dicts(self) -> Iterable[Dict[str, Any]]:
        return map(partial(as_dict, flatten=True), self)

    @overload
    def map(
        self, mapper: Callable[[_DataClass], _DataClass], /
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def map(
        self, type_: Type[_T], mapper: Callable[[_T], _DataClass], /
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def map(
        self, **field_mappers: Callable[[_T], _T]
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def map(
        self, type_: Type[_U], /, **field_mappers: Callable[[_T], _T]
    ) -> DataClassSequence[_DataClass]:
        ...

    def map(
        self,
        type_or_mapper: Optional[
            Union[Callable[[_DataClass], _DataClass], Type[_U]]
        ] = None,
        mapper: Optional[Callable[[_DataClass], _DataClass]] = None,
        /,
        **field_mappers: Callable[[_T], _T],
    ) -> DataClassSequence[_DataClass]:
        _mapper = field_mapper(type_or_mapper, mapper, **field_mappers)
        obj = copy.copy(self)
        obj.__entries__ = list(map(_mapper, self))
        return obj

    @overload
    def filter(
        self, pred: Callable[[_DataClass], bool], /
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def filter(
        self, type_: Type[_T], pred: Callable[[_T], bool], /
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def filter(
        self, **field_preds: Callable[[_T], bool]
    ) -> DataClassSequence[_DataClass]:
        ...

    @overload
    def filter(
        self, type_: Type[_U], /, **field_preds: Callable[[_T], bool]
    ) -> DataClassSequence[_DataClass]:
        ...

    def filter(
        self,
        type_or_pred: Optional[
            Union[Callable[[_DataClass], bool], Type[_U]]
        ] = None,
        pred: Optional[Callable[[_DataClass], bool]] = None,
        /,
        **field_preds: Callable[[_T], bool],
    ) -> DataClassSequence[_DataClass]:
        _pred = field_pred(type_or_pred, pred, **field_preds)
        obj = copy.copy(self)
        obj.__entries__ = list(filter(_pred, self))
        return obj
