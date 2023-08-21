import unittest
import unittest.mock
from unittest.mock import patch
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Internal_Representation.Object import Object


class ProblemTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        pass

    def test_add_list_of_objects(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)
        list_of_objects = [Object('MockOb1'), Object('MockOb2'), Object('MockOb3')]
        problem.add_object(list_of_objects)

        self.assertIn('MockOb1', problem.objects)
        self.assertIn('MockOb2', problem.objects)
        self.assertIn('MockOb3', problem.objects)
