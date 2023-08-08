import unittest
from TestTools.rover_execution import execution_prep
from TestTools.env_setup import env_setup
from Internal_Representation.subtasks import Subtasks
from Solver.Heuristics.partial_order_pruning import PartialOrderPruning


class PartialOrderTests(unittest.TestCase):

    def setUp(self) -> None:
        self.rover_path = "../Examples/Partial_Order/Rover/"
        self.satelite_path = "../Examples/IPC_Tests/satellite01/"

    def test_rover(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "pfile01.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_rover_presolve_setup(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "pfile01.hddl")
        execution_prep(problem, solver)
        search_models = solver.search_models
        self.assertEqual(6, len(search_models))

    def test_ordering_total_ordered_problem(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.satelite_path + "domain2.hddl")
        method = domain.methods['method0']
        self.assertEqual(1, len(method.subtasks.task_orderings))
        self.assertEqual(3, len(method.subtasks.task_orderings[0]))
        self.assertEqual(domain.tasks['activate_instrument'], method.subtasks.task_orderings[0][0].task)
        self.assertEqual(domain.get_modifier('turn_to'), method.subtasks.task_orderings[0][1].task)
        self.assertEqual(domain.get_modifier('take_image'), method.subtasks.task_orderings[0][2].task)

    def test_ordering_creation(self):
        # Test ordering creation function with partial orderings that yield multiple orderings
        orderings = ['and', ['<', 'task0', 'task2'], ['<', 'task1', 'task2'], ['<', 'task2', 'task3']]
        subt = Subtasks(False)
        res = subt._create_orderings(orderings)
        self.assertEqual(2, len(res))
        self.assertTrue(res[0][0].name == "task0" or res[1][0].name == "task0")
        self.assertTrue(res[0][1].name == "task1" or res[1][1].name == "task1")
        self.assertTrue(res[0][0].name == "task1" or res[1][0].name == "task1")
        self.assertTrue(res[0][1].name == "task0" or res[1][1].name == "task0")
        self.assertTrue(res[0][2].name == "task2" and res[1][2].name == "task2")
        self.assertTrue(res[0][3].name == "task3" and res[1][3].name == "task3")

    def test_ordering_creation_2(self):
        # Test ordering creation function with partial orderings that yield multiple orderings
        orderings = ['and', ['<', 'task0', 'task2'], ['<', 'task1', 'task2'], ['<', 'task2', 'task3'], ['<', 'task4', 'task0'], ['<', 'task4', 'task1']]
        subt = Subtasks(False)
        res = subt._create_orderings(orderings)
        self.assertEqual(2, len(res))
        self.assertTrue(res[0][0].name == "task4" and res[1][0].name == "task4")
        self.assertTrue(res[0][1].name == "task0" or res[1][1].name == "task0")
        self.assertTrue(res[0][2].name == "task1" or res[1][2].name == "task1")
        self.assertTrue(res[0][1].name == "task1" or res[1][1].name == "task1")
        self.assertTrue(res[0][2].name == "task0" or res[1][2].name == "task0")
        self.assertTrue(res[0][3].name == "task2" and res[1][3].name == "task2")
        self.assertTrue(res[0][4].name == "task3" and res[1][4].name == "task3")

    def test_ordering_creation_3(self):
        # Test ordering creation function with partial orderings that yield multiple orderings
        orderings = ['and', ['<', 'task0', 'task1'], ['<', 'task1', 'task3'], ['<', 'task2', 'task3'], ['<', 'task3', 'task5'], ['<', 'task4', 'task5'], ['<', 'task5', 'task6']]
        subt = Subtasks(False)
        res = subt._create_orderings(orderings)
        # [0, 1, 2, 3, 4, 5, 6], [0, 1, 2, 4, 3, 5, 6], [0, 1, 4, 2, 3, 5, 6], [0, 2, 1, 3, 4, 5, 6], [0, 2, 1, 4, 3, 5, 6]
        # [0, 2, 4, 1, 3, 5, 6], [0, 4, 1, 2, 3, 5, 6], [0, 4, 2, 1, 3, 5, 6], [2, 0, 1, 3, 4, 5, 6], [2, 0, 1, 4, 3, 5, 6]
        # [2, 0, 4, 1, 3, 5, 6], [2, 4, 0, 1, 3, 5, 6], [4, 0, 1, 2, 3, 5, 6], [4, 0, 2, 1, 3, 5, 6], [4, 2, 0, 1, 3, 5, 6]
        self.assertEqual(15, len(res))

    def test_partial_order_pruning(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "pfile01.hddl")
        solver.set_heuristic(PartialOrderPruning)
        res = solver.solve()
        self.assertNotEqual(None, res)
