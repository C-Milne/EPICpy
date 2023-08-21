import unittest
import unittest.mock
from unittest.mock import patch
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('')
    sys.path.append(os.getcwd())

from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem


class ProblemTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        pass

    def test_add_object(self):
        self.assertEqual(1, 2)
