import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Tests.TestTools.rover_execution import execution_prep
from Tests.TestTools.env_setup import env_setup


class JSHOPSolvingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logistics_path = "Examples/JShop/logistics/"
        self.madrts_path = "Examples/JShop/madrts/"
        self.rover_path = "Examples/JShop/rover/"
        self.rover_test_path = "Tests/TestTools/J-Rover/"

    @unittest.skip
    def test_logistics_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.logistics_path + "logistics.jshop")
        parser.parse_problem(self.logistics_path + "problem.jshop")
        res = solver.solve()
        self.assertEqual(1, 2)

    @unittest.skip
    def test_madrts_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.madrts_path + "madrts.jshop")
        parser.parse_problem(self.madrts_path + "problem.jshop")
        res = solver.solve()
        self.assertEqual(1, 2)

    @unittest.skip
    def test_madrts_execution_walkthrough(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.madrts_path + "madrts.jshop")
        parser.parse_problem(self.madrts_path + "problem.jshop")
        execution_prep(problem, solver)

        solver._Solver__search(True)
        solver._Solver__search(True)
        solver._Solver__search(True)
        search_models = solver.search_models._SearchQueue__Q
        self.assertEqual(1, 2)

    @unittest.skip
    def test_rover_execution(self):
        """This test appears to take a long time to finish"""
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_path + "rover.jshop")
        parser.parse_problem(self.rover_path + "problem.jshop")
        res = solver.solve()
        self.assertEqual(1, 2)
