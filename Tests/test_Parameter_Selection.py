import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Tests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.action_tracker import ActionTracker
from Solver.Parameter_Selection.All_Parameters import AllParameters
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection


class ParameterSelectionTests(unittest.TestCase):

    def setUp(self) -> None:
        self.basic_path_HDDL = "Examples/Basic/"
        self.rover_path_HDDL = "Examples/Rover/"
        self.snake_path = "Tests/TestTools/Snake/"

    def test_select_all_parameters_basic_hddl(self):
        domain, problem, parser, solver = env_setup(True)
        solver.set_parameter_selector(AllParameters)
        parser.parse_domain(self.basic_path_HDDL + "basic.hddl")
        parser.parse_problem(self.basic_path_HDDL + "pb1.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)
        self.assertEqual(ActionTracker(domain.tasks['swap'], {'?x': problem.objects['banjo'],
                                                              '?y': problem.objects['kiwi']}), res.get_progress_tracker().operations_taken[0])
        self.assertEqual(ActionTracker(domain.methods['have_second'], {'?x': problem.objects['banjo'],
                                                                       '?y': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[1])
        self.assertEqual(ActionTracker(domain.actions['drop'], {'?a': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[2])
        self.assertEqual(ActionTracker(domain.actions['pickup'], {'?a': problem.objects['banjo']}),
                         res.get_progress_tracker().operations_taken[3])

    @unittest.skip
    def test_select_all_parameters_rover1_hddl(self):
        domain, problem, parser, solver = env_setup(True)
        solver.set_parameter_selector(AllParameters)
        parser.parse_domain(self.rover_path_HDDL + "domain.hddl")
        parser.parse_problem(self.rover_path_HDDL + "p01.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)

    # @unittest.skip
    def test_select_requirement_selector_rover1_hddl(self):
        domain, problem, parser, solver = env_setup(True)
        solver.set_parameter_selector(RequirementSelection)
        parser.parse_domain(self.rover_path_HDDL + "domain.hddl")
        parser.parse_problem(self.rover_path_HDDL + "p01.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_requirements_forall_1(self):
        domain, problem, parser, solver = env_setup(True)
        solver.set_parameter_selector(RequirementSelection)
        parser.parse_domain(self.snake_path + "domain.hddl")
        parser.parse_problem(self.snake_path + "problem.hddl")
        solver.parameter_selector.presolving_processing(domain, problem)
        method_requirements = domain.get_method('hunt_done').requirements
        # self.assertEqual({'forall-A-1': {'foo': '?a'}}, method_requirements)
        self.assertEqual({'forall-location-1': {'not': {'mouse-at': '?pos'}}}, method_requirements)
