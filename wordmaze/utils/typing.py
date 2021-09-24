from typing import Any, Callable, Type


def isa(type_: Type) -> Callable[[Any], bool]:
    def isinstance_(obj: Any) -> bool:
        return isinstance(obj, type_)

    return isinstance_
