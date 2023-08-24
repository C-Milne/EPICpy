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
        self.domain = Domain(None)
        self.problem = Problem(self.domain)
        self.domain.add_problem(self.problem)

    def test_add_list_of_objects(self):
        list_of_objects = [Object('MockOb1'), Object('MockOb2'), Object('MockOb3')]
        self.problem.add_object(list_of_objects)

        self.assertIn('MockOb1', self.problem.objects)
        self.assertIn('MockOb2', self.problem.objects)
        self.assertIn('MockOb3', self.problem.objects)

    def test_add_initial_task_network_parameter(self):
        self.problem.add_initial_task_network_parameter('MockHTN_TaskParameter',
                                                        'MockHTN_Task_Type')
        self.assertEqual(1, len(self.problem._initial_task_network_parameters))
        self.assertIn('MockHTN_TaskParameter', self.problem._initial_task_network_parameters)
        self.assertEqual('MockHTN_Task_Type', self.problem._initial_task_network_parameters['MockHTN_TaskParameter'])

    def test_add_duplicate_initial_task_network_parameters(self):
        self.problem.add_initial_task_network_parameter('MockHTN_TaskParameter',
                                                        'MockHTN_Task_Type_A')
        self.problem.add_initial_task_network_parameter('MockHTN_TaskParameter',
                                                        'MockHTN_Task_Type_B')
        self.assertEqual(1, len(self.problem._initial_task_network_parameters))
        self.assertIn('MockHTN_TaskParameter', self.problem._initial_task_network_parameters)
        self.assertEqual('MockHTN_Task_Type_B', self.problem._initial_task_network_parameters['MockHTN_TaskParameter'])

    def test_order_subtasks(self):
        self.assertEqual(1, 2)
