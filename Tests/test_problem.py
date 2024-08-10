import unittest
import unittest.mock
from unittest.mock import patch, MagicMock
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Internal_Representation.Object import Object
from Internal_Representation.Type import Type
from Internal_Representation.precondition import Precondition
from Internal_Representation.subtasks import Subtasks
from Internal_Representation.task import Task
from Internal_Representation.reg_parameter import RegParameter
from runner import Runner


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

    def test_get_all_objects(self):
        mock_type = Type('MockType')
        mock_ob1 = Object('MockOb1', mock_type)
        mock_ob2 = Object('MockOb2', mock_type)
        mock_ob3 = Object('MockOb3')
        self.problem.add_object(mock_ob1)
        self.problem.add_object(mock_ob2)
        self.problem.add_object(mock_ob3)
        result = self.problem.get_objects_of_type(None)
        self.assertEqual(3, len(result))
        self.assertIn(mock_ob1, result)
        self.assertIn(mock_ob2, result)
        self.assertIn(mock_ob3, result)

    def test_get_objects_of_type_error(self):
        with self.assertRaises(TypeError) as error:
            self.problem.get_objects_of_type({'Mock': 123})
        self.assertEqual("Unexpected type <class 'dict'>", str(error.exception))

    def test_get_subtasks_none(self):
        res = self.problem.get_subtasks()
        self.assertIsNone(res)

    def test_get_constant(self):
        mock_const = Object('MockConst')
        self.domain.add_constant(mock_const)
        result = self.problem.get_constant('MockConst')
        self.assertEqual(mock_const, result)

    def test_get_constant_error(self):
        with self.assertRaises(KeyError) as error:
            self.problem.get_constant('MockFakeConst')
        self.assertEqual("'Constant MockFakeConst not found!'", str(error.exception))

    def test_has_goal_conditions_false(self):
        result = self.problem.has_goal_conditions()
        self.assertEqual(False, result)

    def test_has_goal_conditions_true(self):
        mock_goal_conditions = Precondition('')
        self.problem.add_goal_conditions(mock_goal_conditions)

        result = self.problem.has_goal_conditions()
        self.assertEqual(True, result)

    def test_has_initial_task_network_parameters(self):
        self.problem.add_initial_task_network_parameter('MockInitialTNParameter', 'Mock')
        self.assertEqual(True, self.problem.has_initial_task_network_parameters())

    def test_ground_initial_subtasks_calculate_parameter_combinations(self):
        mock_type1 = Type('MockType1')
        mock1_ob1 = Object('Mock1_ob1', mock_type1)
        mock1_ob2 = Object('Mock1_ob2', mock_type1)

        mock_type2 = Type('MockType2')
        mock2_ob1 = Object('Mock2_ob1', mock_type2)
        mock2_ob2 = Object('Mock2_ob2', mock_type2)

        self.domain.add_type(mock_type1)
        self.domain.add_type(mock_type2)

        self.problem.add_object(mock1_ob1)
        self.problem.add_object(mock1_ob2)
        self.problem.add_object(mock2_ob1)
        self.problem.add_object(mock2_ob2)

        self.problem.add_initial_task_network_parameter('MockInitialHTNParameter1', 'MockType1')
        self.problem.add_initial_task_network_parameter('MockInitialHTNParameter2', 'MockType2')

        """
        In this example we have defined two types - MockType1 & MockType2
        We have defined two objects for each of these types
        We have also defined two initial task network parameters - MockInitialHTNParameter1 & MockInitialHTNParameter2
        These parameters have the type, MockType1 and MockType2 respectively
        
        We want to find all combinations of objects which satisfy these parameters.
        
        resulting_parameters_ordering: This is the order that the parameter names are listed in the problem file
        resulting_combinations: This is the list of possible combinations
        """
        resulting_parameters_ordering, resulting_combinations = (
            self.problem._ground_initial_subtasks_calculate_parameter_combinations())
        self.assertEqual(['MockInitialHTNParameter1', 'MockInitialHTNParameter2'], resulting_parameters_ordering)
        self.assertEqual(
            [(mock1_ob1, mock2_ob1), (mock1_ob1, mock2_ob2), (mock1_ob2, mock2_ob1), (mock1_ob2, mock2_ob2)],
            resulting_combinations)

    def test_ground_initial_subtasks(self):
        mock_type1 = Type('MockType1')
        mock1_ob1 = Object('Mock1_ob1', mock_type1)
        mock1_ob2 = Object('Mock1_ob2', mock_type1)

        mock_type2 = Type('MockType2')
        mock2_ob1 = Object('Mock2_ob1', mock_type2)
        mock2_ob2 = Object('Mock2_ob2', mock_type2)

        self.domain.add_type(mock_type1)
        self.domain.add_type(mock_type2)

        self.problem.add_object(mock1_ob1)
        self.problem.add_object(mock1_ob2)
        self.problem.add_object(mock2_ob1)
        self.problem.add_object(mock2_ob2)

        self.problem.add_initial_task_network_parameter('MockInitialHTNParameter1', 'MockType1')
        self.problem.add_initial_task_network_parameter('MockInitialHTNParameter2', 'MockType2')

        self.problem._ground_initial_subtasks_calculate_parameter_combinations = MagicMock(
            return_value=(['MockInitialHTNParameter1', 'MockInitialHTNParameter2'],
                          [(mock1_ob1, mock2_ob1), (mock1_ob1, mock2_ob2), (mock1_ob2, mock2_ob1),
                           (mock1_ob2, mock2_ob2)]))

        mock_task1 = Task('MockTask1', [RegParameter('?MP1', mock_type1)])
        mock_task2 = Task('MockTask2', [RegParameter('?MP2', mock_type2)])
        mock_task3 = Task('MockTask3', [RegParameter('?MP3', mock_type1),
                                        RegParameter('?MP4', mock_type2)])

        mock_subtasks = Subtasks(False)
        mock_subtasks.add_subtask('task1', mock_task1, [RegParameter('MockInitialHTNParameter1')])
        mock_subtasks.add_subtask('task2', mock_task2, [RegParameter('MockInitialHTNParameter2')])
        mock_subtasks.add_subtask('task3', mock_task3, [RegParameter('MockInitialHTNParameter1'),
                                                        RegParameter('MockInitialHTNParameter2')])

        for subtask in mock_subtasks.tasks:
            i = 0
            l = len(subtask.parameters)
            while i < l:
                p = subtask.parameters[i]
                subtask.parameters[i] = p.name
                i += 1

        self.problem.add_subtasks(mock_subtasks)
        self.problem.ground_initial_subtasks()
        subtasks_before_ordering = self.problem._subtasks_before_ordering

        subtasks_0 = subtasks_before_ordering[0]
        self.assertEqual('MockTask1-Mock1_ob1', str(subtasks_0.tasks[0]))
        self.assertEqual('MockTask2-Mock2_ob1', str(subtasks_0.tasks[1]))
        self.assertEqual('MockTask3-Mock1_ob1-Mock2_ob1', str(subtasks_0.tasks[2]))

        subtasks_1 = subtasks_before_ordering[1]
        self.assertEqual('MockTask1-Mock1_ob1', str(subtasks_1.tasks[0]))
        self.assertEqual('MockTask2-Mock2_ob2', str(subtasks_1.tasks[1]))
        self.assertEqual('MockTask3-Mock1_ob1-Mock2_ob2', str(subtasks_1.tasks[2]))

        subtasks_2 = subtasks_before_ordering[2]
        self.assertEqual('MockTask1-Mock1_ob2', str(subtasks_2.tasks[0]))
        self.assertEqual('MockTask2-Mock2_ob1', str(subtasks_2.tasks[1]))
        self.assertEqual('MockTask3-Mock1_ob2-Mock2_ob1', str(subtasks_2.tasks[2]))

        subtasks_3 = subtasks_before_ordering[3]
        self.assertEqual('MockTask1-Mock1_ob2', str(subtasks_3.tasks[0]))
        self.assertEqual('MockTask2-Mock2_ob2', str(subtasks_3.tasks[1]))
        self.assertEqual('MockTask3-Mock1_ob2-Mock2_ob2', str(subtasks_3.tasks[2]))
