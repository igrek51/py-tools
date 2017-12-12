#!/usr/bin/python
# -*- coding: utf-8 -*-
from utilframe_1_2 import *

def test_splitLines():
	assert list(splitLines('a\nb\nc')) == ['a', 'b', 'c']
	assert list(splitLines('\na\n\n')) == ['a']
	assert list(splitLines('\n\n\n')) == []
	assert list(splitLines('')) == []
	assert list(splitLines('a\n\n\r\nb')) == ['a', 'b']

