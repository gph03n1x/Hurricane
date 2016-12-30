#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.utils import *


class TestUtils(unittest.TestCase):

    def test_zip_old_logs(self):
        # TODO: 
        pass


suite = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
unittest.TextTestRunner(verbosity=2).run(suite)
