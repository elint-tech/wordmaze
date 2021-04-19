#!/usr/bin/env python

from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent

VERSION = '0.1.0'

setup(
    name='wordmaze',
    version=VERSION,

    description="Words and textboxes made amazing",
    long_description=Path(here, 'README.md').read_text(),
    long_description_content_type="text/markdown",

    license='MIT',
    author='elint-tech',
    author_email='contato@elint.com.br',

    url='https://github.com/elint-tech/wordmaze/',
    download_url=f'https://github.com/elint-tech/wordmaze/dist/wordmaze-{VERSION}.tar.gz',

    install_requires=Path(here, 'requirements.txt').read_text().splitlines(),
    packages=find_packages(),

    keywords=[
        'wordmaze',
        'ocr',
        'pdf',
        'word',
        'words',
        'text',
        'textbox',
        'textboxes'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ]
)
