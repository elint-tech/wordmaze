import textwrap
from functools import partial
from typing import Any, Callable, Dict, Generic, Iterable, List, TypeVar

import funcy
from dataclassy import DataClass, asdict, astuple, values
from dataclassy.functions import is_dataclass_instance, replace

from wordmaze.utils.sequences import MutableSequence

_DataClass = TypeVar('_DataClass', bound=DataClass)


def as_dict(
        obj: DataClass,
        flatten: bool = False
) -> Dict[str, Any]:
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


def as_tuple(
        obj: DataClass,
        flatten: bool = False
) -> tuple:
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


def field_mapper(
        *mapper: Callable[[_DataClass], _DataClass],
        **field_mappers: Callable[[Any], Any]
) -> Callable[[_DataClass], _DataClass]:
    if mapper and field_mappers:
        raise TypeError(textwrap.dedent(
            '''
            *field_mapper* accepts either a mapper or keyworded mappers. For instance:
                field_mapper(lambda textbox: process_textbox(textbox))
                field_mapper(
                    x1=lambda x1: x1 + 5,
                    x2=lambda x2: x2**2,
                    text=lambda text: text.upper()
                )
            '''
        ))

    if field_mappers:
        def _mapper(obj: _DataClass) -> _DataClass:
            obj_dict = as_dict(obj)

            keys_diff = frozenset(field_mappers).difference(obj_dict)
            if keys_diff:
                raise ValueError(
                    f'fields {list(keys_diff)} do not exist in object'
                    f' {obj} from the class {type(obj)}.'
                )

            obj_dict = funcy.project(obj_dict, field_mappers)
            changes = {
                field_name: _field_mapper(obj_dict[field_name])
                for field_name, _field_mapper in field_mappers.items()
            }

            return replace(
                obj,
                **changes
            )
    else:
        _mapper = mapper[0]

    return _mapper


def field_pred(
        *pred: Callable[[_DataClass], bool],
        **field_preds: Callable[[Any], bool]
) -> Callable[[_DataClass], bool]:
    if pred and field_preds:
        raise TypeError(textwrap.dedent(
        '''
        invalid call. *field_pred* accepts either a pred or keyworded preds. For instance:
        field_pred(lambda textbox: process_textbox(textbox))
        field_pred(
            x1=lambda x1: x1 >= 0,
            x2=lambda x2: (x2 % 2)==0,
            text=lambda text: text.isdigit()
        )
        '''))

    if field_preds:
        def _pred(obj: _DataClass) -> bool:
            obj_dict = as_dict(obj)

            keys_diff = frozenset(field_preds).difference(obj_dict)
            if keys_diff:
                raise ValueError(
                    f'fields {list(keys_diff)} do not exist in object'
                    f' {obj} from the class {type(obj)}.'
                )

            obj_dict = funcy.project(obj_dict, field_preds)
            preds = (
                _field_pred(obj_dict[field_name])
                for field_name, _field_pred in field_preds.items()
            )

            return all(preds)
    else:
        _pred = pred[0]

    return _pred


class DataClassSequence(MutableSequence[_DataClass]):
    def __init__(self, entries: Iterable[_DataClass] = ()) -> None:
        super().__init__(entries)

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

    def map(
            self,
            *mapper: Callable[[_DataClass], _DataClass],
            **field_mappers: Callable[[Any], Any]
    ) -> Iterable[_DataClass]:
        _mapper = field_mapper(*mapper, **field_mappers)
        return map(_mapper, self)

    def filter(
            self,
            *pred: Callable[[_DataClass], bool],
            **field_preds: Callable[[Any], bool]
    ) -> Iterable[_DataClass]:
        _pred = field_pred(*pred, **field_preds)
        return filter(_pred, self)
