import pytest
from dataclassy import dataclass

from wordmaze import TextBox
from wordmaze.utils.dataclasses import (DataClassSequence, as_dict, as_tuple,
                                        field_mapper, field_pred)


def test_as_dict():
    @dataclass
    class Text:
        text: str

    @dataclass
    class TextPage:
        index: int
        contents: Text

    text = Text('In a hole in the ground there lived a hobbit')
    text_page = TextPage(index=0, contents=text)

    text_page_dict = as_dict(text_page, flatten=False)
    text_page_dict_ans = {
        'index': 0,
        'contents': {
            'text': 'In a hole in the ground there lived a hobbit'
        }
    }
    assert text_page_dict == text_page_dict_ans

    flat_text_page_dict = as_dict(text_page, flatten=True)
    flat_text_page_dict_ans = {
        'index': 0,
        'text': 'In a hole in the ground there lived a hobbit'
    }
    assert flat_text_page_dict == flat_text_page_dict_ans


def test_as_tuple():
    @dataclass
    class Text:
        text: str

    @dataclass
    class TextPage:
        index: int
        contents: Text

    text = Text('In a hole in the ground there lived a hobbit')
    text_page = TextPage(index=0, contents=text)

    text_page_tuple = as_tuple(text_page, flatten=False)
    text_page_tuple_ans = (
        0,
        ('In a hole in the ground there lived a hobbit',)
    )
    assert text_page_tuple == text_page_tuple_ans

    flat_text_page_tuple = as_tuple(text_page, flatten=True)
    flat_text_page_tuple_ans = (
        0,
        'In a hole in the ground there lived a hobbit'
    )
    assert flat_text_page_tuple == flat_text_page_tuple_ans


def test_field_mapper():
    textbox = TextBox(
        x1=0,
        x2=1,
        y1=10,
        y2=11,
        text='One ring to rule them all',
        confidence=10
    )

    flipper = field_mapper(
        lambda tbox: TextBox(
            x1=tbox.x2,
            x2=tbox.x1,
            y1=tbox.y2,
            y2=tbox.y1,
            text=tbox.text[::-1],
            confidence=1/tbox.confidence
        )
    )
    assert flipper(textbox) == TextBox(
        x1=1,
        x2=0,
        y1=11,
        y2=10,
        text='lla meht elur ot gnir enO',
        confidence=0.1
    )

    padder = field_mapper(
        x1=lambda x1: x1-10,
        x2=lambda x2: x2+10
    )
    assert padder(textbox) == TextBox(
        x1=-10,
        x2=11,
        y1=10,
        y2=11,
        text='One ring to rule them all',
        confidence=10
    )

    with pytest.raises(TypeError):
        field_mapper(
            lambda tbox: TextBox(
                x1=tbox.x2,
                x2=tbox.x1,
                y1=tbox.y2,
                y2=tbox.y1,
                text=tbox.text[::-1],
                confidence=1/tbox.confidence
            ),
            x1=lambda x1: x1-10,
            x2=lambda x2: x2+10
        )


def test_field_pred():
    textbox1 = TextBox(
        x1=0,
        x2=1,
        y1=10,
        y2=11,
        text='One ring to rule them all',
        confidence=10
    )
    textbox2 = TextBox(
        x1=0,
        x2=1,
        y1=10,
        y2=11,
        text='One ring to rule no one',
        confidence=1
    )

    is_long_confident = field_pred(
        lambda tbox: tbox.confidence > 5 and len(tbox.text) > 5
    )
    assert is_long_confident(textbox1)
    assert not is_long_confident(textbox2)

    is_long_confident = field_pred(
        confidence=lambda conf: conf > 5,
        text=lambda txt: len(txt) > 5
    )
    assert is_long_confident(textbox1)
    assert not is_long_confident(textbox2)

    with pytest.raises(TypeError):
        field_pred(
            lambda tbox: tbox.confidence > 5 and len(tbox.text) > 5,
            confidence=lambda conf: conf > 5,
            text=lambda txt: len(txt) > 5
        )


def test_DataClassSequence():
    @dataclass
    class Example:
        i: int
        s: str

    class Examples(DataClassSequence[Example]):
        pass

    examples = Examples([
        Example(i=0, s='zero'),
        Example(i=1, s='one')
    ])

    assert Example(i=0, s='zero') in examples

    assert Example(i=2, s='two') not in examples
    examples.append(Example(i=2, s='two'))
    assert Example(i=2, s='two') in examples
    assert len(examples) == 3
    assert list(examples) == [
        Example(i=0, s='zero'),
        Example(i=1, s='one'),
        Example(i=2, s='two')
    ]
    assert examples[2] == Example(i=2, s='two')
