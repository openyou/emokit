# -*- encoding: utf-8 -*-
import unittest

from emokit.emotiv import Emotiv


class TestEmotiv(unittest.TestCase):
    def test_emotiv(self):
        with Emotiv() as emotiv:
            print(True)
