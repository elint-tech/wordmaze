from typing import Any, Dict

import funcy
from dataclassy import DataClass, asdict, astuple, values
from dataclassy.functions import is_dataclass_instance


def as_dict(
    obj: DataClass,
    flatten: bool = False
) -> Dict[str, Any]:
    if flatten:
        return funcy.merge(*(
            (
                as_dict(field, flatten=flatten)
                if is_dataclass_instance(field)
                else {field_name: field}
            )
            for field_name, field in values(obj).items()
        ))
    else:
        return asdict(obj)


def as_tuple(
    obj: DataClass,
    flatten: bool = False
) -> tuple:
    if flatten:
        return funcy.merge(*(
            (
                as_tuple(field, flatten=flatten)
                if is_dataclass_instance(field)
                else (field,)
            )
            for field in obj
        ))
    else:
        return astuple(obj)
