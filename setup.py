#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'AutoCython-jianjun',
    version = '1.2.9',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/AutoCython',
    description = u'自动Cython，使用Cython批量编译.py文件为.pyd文件！',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["AutoCython"],
    install_requires = [],
    entry_points={
        'console_scripts': [
            'AutoCython=AutoCython:main'
        ],
    },
)