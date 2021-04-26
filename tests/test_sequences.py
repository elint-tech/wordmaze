from wordmaze.utils.sequences import MutableSequence


def test_MutableSequence():
    class IntSeq(MutableSequence[int]):
        pass

    seq = IntSeq([3, 14, 15])
    assert len(seq) == 3
    assert seq[2] == 15
    assert 3 in seq
    assert 0 not in seq
