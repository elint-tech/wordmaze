import pytest

from wordmaze.wordmaze import Origin, Shape, TextBox, WordMaze
from wordmaze import Page

def test_Page():
    page = Page(
        shape=Shape(height=100, width=80),
        origin=Origin.TOP_LEFT,
        entries=[
            TextBox(
                x1=10,
                x2=50,
                y1=20,
                y2=30,
                text='Hello',
                confidence=0.7
            ),
            TextBox(
                x1=60,
                x2=75,
                y1=80,
                y2=85,
                text='Bye',
                confidence=0.6
            )
        ]
    )

    assert list(page) == [
        TextBox(
            x1=10,
            x2=50,
            y1=20,
            y2=30,
            text='Hello',
            confidence=0.7
        ),
        TextBox(
            x1=60,
            x2=75,
            y1=80,
            y2=85,
            text='Bye',
            confidence=0.6
        )
    ]
    assert page.shape.height == 100
    assert page.shape.width == 80
    assert page.origin is Origin.TOP_LEFT

    padded = page.map(
        x1=lambda x1: x1 - 2,
        x2=lambda x2: x2 + 2,
        y1=lambda y1: y1 - 2,
        y2=lambda y2: y2 + 2
    )
    assert padded.shape == page.shape
    assert list(padded) == [
        TextBox(
            x1=8,
            x2=52,
            y1=18,
            y2=32,
            text='Hello',
            confidence=0.7
        ),
        TextBox(
            x1=58,
            x2=77,
            y1=78,
            y2=87,
            text='Bye',
            confidence=0.6
        )
    ]

    confident = page.filter(confidence=lambda conf: conf > 0.65)
    assert confident.shape == page.shape
    assert list(confident) == [
        TextBox(
            x1=10,
            x2=50,
            y1=20,
            y2=30,
            text='Hello',
            confidence=0.7
        )
    ]

    rebased = page.rebase(Origin.BOTTOM_LEFT)
    assert rebased.shape == page.shape
    assert rebased.origin is Origin.BOTTOM_LEFT
    assert list(rebased) == [
        TextBox(
            x1=10,
            x2=50,
            y1=70,
            y2=80,
            text='Hello',
            confidence=0.7
        ),
        TextBox(
            x1=60,
            x2=75,
            y1=15,
            y2=20,
            text='Bye',
            confidence=0.6
        )
    ]

    not_rebased = page.rebase(page.origin)
    assert not_rebased == page

    with pytest.raises(NotImplementedError):
        page.rebase('invalid')


def test_wordmaze():
    maze = WordMaze([
        Page(
            shape=Shape(height=100, width=80),
            origin=Origin.TOP_LEFT,
            entries=[
                TextBox(
                    x1=10,
                    x2=50,
                    y1=20,
                    y2=30,
                    text='Hello',
                    confidence=0.7
                ),
                TextBox(
                    x1=60,
                    x2=75,
                    y1=80,
                    y2=85,
                    text='Bye',
                    confidence=0.6
                )
            ]
        ),
        Page(
            shape=Shape(height=50, width=200),
            origin=Origin.BOTTOM_LEFT,
            entries=[
                TextBox(
                    x1=110,
                    x2=180,
                    y1=40,
                    y2=45,
                    text='Hey ho',
                    confidence=0.2
                )
            ]
        )
    ])

    assert maze.shapes == (
        Shape(height=100, width=80),
        Shape(height=50, width=200)
    )

    assert list(maze.tuples()) == [
        (0, 10, 50, 20, 30, 'Hello', 0.7),
        (0, 60, 75, 80, 85, 'Bye', 0.6),
        (1, 110, 180, 40, 45, 'Hey ho', 0.2)
    ]

    assert list(maze.dicts()) == [
        {'page': 0, 'x1': 10, 'x2': 50, 'y1': 20, 'y2': 30, 'text': 'Hello', 'confidence': 0.7},
        {'page': 0, 'x1': 60, 'x2': 75, 'y1': 80, 'y2': 85, 'text': 'Bye', 'confidence': 0.6},
        {'page': 1, 'x1': 110, 'x2': 180, 'y1': 40, 'y2': 45, 'text': 'Hey ho', 'confidence': 0.2}
    ]

    assert list(maze.map(
        x1=lambda x1: x1-5,
        x2=lambda x2: x2+10,
        y1=lambda y1: y1-10,
        y2=lambda y2: y2+5,
    ).tuples()) == list(WordMaze([
        Page(
            shape=Shape(height=100, width=80),
            origin=Origin.TOP_LEFT,
            entries=[
                TextBox(
                    x1=10-5,
                    x2=50+10,
                    y1=20-10,
                    y2=30+5,
                    text='Hello',
                    confidence=0.7
                ),
                TextBox(
                    x1=60-5,
                    x2=75+10,
                    y1=80-10,
                    y2=85+5,
                    text='Bye',
                    confidence=0.6
                )
            ]
        ),
        Page(
            shape=Shape(height=50, width=200),
            origin=Origin.BOTTOM_LEFT,
            entries=[
                TextBox(
                    x1=110-5,
                    x2=180+10,
                    y1=40-10,
                    y2=45+5,
                    text='Hey ho',
                    confidence=0.2
                )
            ]
        )
    ]).tuples())

    assert list(maze.filter(
        confidence=lambda conf: conf >= 0.65
    ).tuples()) == list(WordMaze([
        Page(
            shape=Shape(height=100, width=80),
            origin=Origin.TOP_LEFT,
            entries=[
                TextBox(
                    x1=10,
                    x2=50,
                    y1=20,
                    y2=30,
                    text='Hello',
                    confidence=0.7
                )
            ]
        ),
        Page(
            shape=Shape(height=50, width=200),
            origin=Origin.BOTTOM_LEFT,
            entries=[]
        )
    ]).tuples())
