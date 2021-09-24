from wordmaze.utils.typing import isa


def test_isa() -> None:
    assert isa(float)(10.5)
    assert isa(str)('string')
    assert not isa(int)('string')

    is_int = isa(int)
    assert is_int(10)
    assert is_int(False)
    assert not is_int(-3.14)
