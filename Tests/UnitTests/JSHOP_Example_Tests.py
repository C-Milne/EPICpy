import unittest
from Tests.UnitTests.TestTools.rover_execution import execution_prep
from Tests.UnitTests.TestTools.env_setup import env_setup


class JSHOPSolvingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logistics_path = "../Examples/JShop/logistics/"
        self.madrts_path = "../Examples/JShop/madrts/"
        self.rover_path = "../Examples/JShop/rover/"
        self.rover_test_path = "TestTools/J-Rover/"

    def test_logistics_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.logistics_path + "logistics")
        parser.parse_problem(self.logistics_path + "problem")
        res = solver.solve()
        self.assertEqual(1, 2)

    def test_madrts_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.madrts_path + "madrts")
        parser.parse_problem(self.madrts_path + "problem")
        res = solver.solve()
        self.assertEqual(1, 2)

    def test_madrts_execution_walkthrough(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.madrts_path + "madrts")
        parser.parse_problem(self.madrts_path + "problem")
        execution_prep(problem, solver)

        solver._Solver__search(True)
        solver._Solver__search(True)
        solver._Solver__search(True)
        search_models = solver.search_models._SearchQueue__Q
        self.assertEqual(1, 2)

    def test_rover_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_path + "rover")
        parser.parse_problem(self.rover_path + "problem")
        res = solver.solve()
        self.assertEqual(1, 2)
