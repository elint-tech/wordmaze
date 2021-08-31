WordMaze
[![PyPI version fury.io](https://img.shields.io/pypi/v/wordmaze?color=blue)](https://github.com/elint-tech/wordmaze)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/wordmaze)](https://github.com/elint-tech/wordmaze)
===

*Words and textboxes made amazing.*

## About

WordMaze is a standardized format for text extracted from documents.

When designing [OCR](https://www.wikiwand.com/en/Optical_character_recognition) engines, developers have to decide how to give their clients the list of extracted textboxes, including their position in the page, the text they contain and the confidence associated with that extraction.

Many patterns arise in the wild, for instance:
```py
(x1, x2, y1, y2, text, confidence) # a flat tuple
((x1, y1), (x2, y2), text, confidence) # nested tuples
{'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'text': text, 'confidence': confidence} # a dict
{'x': x1, 'y': y1, 'w': width, 'h': height, 'text': text, 'conf': confidence} # another dict
... # and many others
```

With WordMaze, textboxes are defined using a unified interface:
```py
from wordmaze import TextBox

textbox = TextBox(
	x1=x1,
	x2=x2,
	y1=y1,
	y2=y2,
	text=text,
	confidence=confidence
)
# or
textbox = TextBox(
	x1=x,
	width=w,
	y1=y,
	height=h,
	text=text,
	confidence=conf
)
```

## Usage

Perhaps the best example of usage is [`pdfmap.PDFMaze`](https://github.com/elint-tech/pdfmap/blob/e5b3434a63729ba5a737201d93a146f2e0e5ad7a/pdfmap/pdfmaze.py), the first application of WordMaze in a public repository.

The exact expected behaviour of every piece of code in WordMaze can be checked out at the [tests folder](https://github.com/elint-tech/wordmaze/tree/main/tests).

There are three main groups of objects defined in WordMaze:

### Textboxes

#### `Box`es

The first and most fundamental [(data)class](https://pypi.org/project/dataclassy/) is the `Box`, which contains only positional information of a textbox inside a document's page:
```py
from wordmaze import Box

box1 = Box(x1=3, x2=14, y1=15, y2=92) # using coordinates
box2 = Box(x1=3, width=11, y1=15, height=77) # using coordinates and sizes
box3 = Box(x1=3, x2=14, y2=92, height=77) # mixing everything
```

We enforce `x1<=x2` and `y1<=y2` (if `x1>x2`, for instance, their values are automatically swapped upon initialization). Whether `(y1, y2)` means `(top, bottom)` or `(bottom, top)` depends on the context.

`Box`es have some interesting attributes to facilitate further calculation using them:
```py
from wordmaze import Box

box = Box(x1=1, x2=3, y1=10, y2=22)
# coordinates:
print(box.x1) # 1
print(box.x2) # 3
print(box.y1) # 10
print(box.y2) # 22
# sizes:
print(box.height) # 12 
print(box.width) # 2
# midpoints:
print(box.xmid) # 2
print(box.ymid) # 16
```

#### `Textbox`es

To include textual information in a textbox, use a `TextBox`:
```py
from wordmaze import TextBox

textbox = TextBox(
	# Box arguments:
	x1=3,
	x2=14,
	y1=15,
	height=77,
	# textual content:
	text='Dr. White.',
	# confidence with which this text was extracted:
	confidence=0.85 # 85% confidence
)
```

Note that `TextBox`es inherit from `Box`es, so you can inspect `.x1`, `.width` and so on as shown previously. Moreover, you have two more properties:
```py
# textbox from the previous example
print(textbox.text) # Dr. White.
print(textbox.confidence) # 0.85
```

#### `PageTextBox`es

If you also wish to include the page number from which your textbox was extracted, you can use a `PageTextBox`:
```py
from wordmaze import PageTextBox

textbox = PageTextBox(
	# TextBox arguments:
	x1=2,
	x2=10,
	y1=5,
	height=20,
	text='Sichermann and Sichelero and the same person!',
	confidence=0.6,
	# page info:
	page=3 # this textbox was extracted from the 4th page of the document
)
print(textbox.page) # 3
```

Note that page counting starts from `0` as is common in Python, so that page #3 is the 4th page of the document.

### Pages

#### The basics

`Page`s are a representation of a document's page. They contain information regarding their size, their coordinate system's origin and their textboxes. For instance:
```py
from wordmaze import Page, Shape, Origin

page = Page(
	shape=Shape(height=210, width=297), # A4 page size in mm
	origin=Origin.TOP_LEFT
)
print(page.shape.height) # 210
print(page.shape.width) # 297
print(page.origin) # Origin.TOP_LEFT
```

A `Page` is a [`MutableSequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence) of `TextBox`es:
```py
page = Page(
	shape=Shape(height=210, width=297), # A4 page size in mm
	origin=Origin.TOP_LEFT,
	entries=[ # define textboxes at initialization
		TextBox(...),
		TextBox(...),
		...
	]
)

page.append(TextBox(...)) # list-like append

for textbox in page: # iteration
	assert isinstance(textbox, TextBox)

print(page[3]) # 4th textbox
```

#### Different origins

There are two `Origin`s your page may have:
- `Origin.TOP_LEFT`: `y==0` means top, `y==page.shape.height` means bottom;
- `Origin.BOTTOM_LEFT`: `y==0` means bottom, `y==page.shape.height` means top;

If one textbox provider returned textboxes in `Origin.BOTTOM_LEFT` coordinates, but you'd like to have them in `Origin.TOP_LEFT` coordinates, you can use `Page.rebase` as follows:
```py
bad_page = Page(
	shape=Shape(width=10, height=10),
	origin=Origin.BOTTOM_LEFT,
	entries=[
		TextBox(
			x1=2,
			x2=3,
			y1=7,
			y2=8,
			text='Lofi defi',
			confidence=0.99
		)
	]
)

nice_page = bad_page.rebase(Origin.TOP_LEFT)
assert nice_page.shape == bad_page.shape # rebasing preserves page shape
print(nice_page[0].y1, nice_page[0].y2) # 2 3
```

#### Transforming and filtering `TextBox`es

You can easily modify and filter out `TextBox`es contained in a `Page` using `Page.map` and `Page.filter`, which behave like [`map`](https://docs.python.org/3/library/functions.html#map) and [`filter`](https://docs.python.org/3/library/functions.html#filter) where the iterable is fixed and equal to the page's textboxes:
```py
page = Page(...)

def pad(textbox: TextBox, horizontal, vertical) -> TextBox:
	return TextBox(
		x1=textbox.x1 - horizontal,
		x2=textbox.x2 + horizontal,
		y1=textbox.y1 - vertical,
		y2=textbox.y2 + vertical,
		text=textbox.text,
		confidence=textbox.confidence
	)

# get a new page with textboxes padded by 3 to the left and to the right
# and by 5 to the top and to the bottom
padded_page = page.map(lambda textbox: pad(textbox, horizontal=3, vertical=5))

# filters out textboxes with low confidence
good_page = padded_page.filter(lambda textbox: textbox.confidence >= 0.25)
```

`Page.map` and `Page.filter` also accept keywords. Each keyword accepts a function that accepts the respective property and operates on it. Better shown in code. The previous padding and filtering can be equivalently written as:
```py
# get a new page with textboxes padded by 3 to the left and to the right
# and by 5 to the top and to the bottom
padded_page = page.map(
	x1=lambda x1: x1-3,
	x2=lambda x2: x2+3,
	y1=lambda y1: y1-5,
	y2=lambda y2: y2+5,
)

# filters out textboxes with low confidence
good_page = padded_page.filter(confidence=lambda conf: conf >= 0.25)
```

#### `tuple`s and `dict`s

You can also convert page's textboxes to `tuple`s or `dict`s with `Page.tuples` and `Page.dicts`:
```py
page = Page(...)
for tpl in page.tuples():
	# prints a tuple in the form
	# (x1, x2, y1, y2, text, confidence)
	print(tpl)

for dct in page.dicts():
	# prints a dict in the form
	# {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'text': text, 'confidence': confidence}
	print(dct)
```

### `WordMaze`s

The top-level class from WordMaze is, of course, a `WordMaze`. `WordMaze`s are simply sequences of `Page`s:
```py
from wordmaze import WordMaze

wm = WordMaze([
	Page(...),
	Page(...),
	...
])

for page in wm: # iterating
	print(page.shape)

first_page = wm[0] # indexing
```

`WordMaze` objects also provide a `WordMaze.map` and a `WordMaze.filter` functions, which work the same thing that `Page.map` and `Page.filter` do.

If you wish to access `WordMaze`'s pages shapes, there is the property `WordMaze.shapes`, which is a `tuple` satisfying `wm.shapes[N] == wm[N].shape`.

Additionally, you can iterate over `WordMaze`'s textboxes in two ways:
```py
wm = WordMaze(...)

# 1
for page in wm:
	for textbox in page:
		print(textbox)

# 2
for textbox in wm.textboxes():
	print(textbox)
```
The main difference between #1 and #2 is that the textboxes in #1 are instances of `TextBox`, whereas the ones in #2 are `PageTextBox`es including their containing page index.

`WordMaze` objects also have a `WordMaze.tuples` and a `WordMaze.dicts` which behave just like their `Page` counterpart except that they also return their page's number:
```py
wm = WordMaze(...)
for tpl in wm.tuples():
	# prints a tuple in the form
	# (x1, x2, y1, y2, text, confidence, page_number)
	print(tpl)

for dct in wm.dicts():
	# prints a dict in the form
	# {'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'text': text, 'confidence': confidence, 'page': page_number}
	print(dct)
```

## Installing

Install WordMaze from [PyPI](https://pypi.org/project/wordmaze/):
```
pip install wordmaze
```

## Projects using WordMaze

* [elint-tech/pdfmap](https://github.com/elint-tech/pdfmap): easily extract textboxes from PDF files.
