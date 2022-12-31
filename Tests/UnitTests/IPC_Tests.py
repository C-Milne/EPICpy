import unittest
from Solver.Solving_Algorithms.solver import Solver
from Solver.Heuristics.hamming_distance import HammingDistance
from Tests.UnitTests.TestTools.env_setup import env_setup


class IPCTests(unittest.TestCase):

    def setUp(self) -> None:
        self.IPC_Tests_path = "../Examples/IPC_Tests/"

    def test_1_empty_method(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test01_empty_method/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test01_empty_method/problem.hddl")
        plan = solver.solve()
        solver.output(plan)

        self.assertEqual(0, len(plan.get_progress_tracker().actions_taken))
        self.assertEqual("State is empty.", str(plan.current_state))
        self.assertEqual(0, len(plan.search_modifiers))

    def test_2_forall(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test02_forall/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test02_forall/problem.hddl")
        plan = solver.solve()
        solver.output(plan)
        self.assertIsNotNone(plan)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))

    def test_3_forall1(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test03_forall1/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test03_forall1/problem.hddl")
        plan = solver.solve()
        solver.output(plan)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken[0].parameters_used))
        self.assertEqual(problem.objects['f'], plan.get_progress_tracker().actions_taken[0].parameters_used['?b'])

    def test_4_no_abstracts(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test04_no_abstracts/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test04_no_abstracts/problem.hddl")
        plan = solver.solve()
        solver.output(plan)

        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))
        self.assertEqual(1, len(plan.get_progress_tracker().operations_taken))
        self.assertEqual(domain.actions['noop'], plan.get_progress_tracker().actions_taken[0].mod)
        self.assertEqual(domain.actions['noop'], plan.get_progress_tracker().operations_taken[0].mod)
        self.assertEqual("State is empty.", str(plan.current_state))
        self.assertEqual(0, len(plan.search_modifiers))

    def test_5_constants_in_domain(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test05_constants_in_domain/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test05_constants_in_domain/problem.hddl")
        plan = solver.solve()
        solver.output(plan)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))
        self.assertEqual(domain.actions['noop'], plan.get_progress_tracker().actions_taken[0].mod)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken[0].parameters_used))
        self.assertEqual(problem.objects['a'], plan.get_progress_tracker().actions_taken[0].parameters_used['?a'])

    def test_6_synonymes(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test06_synonymes/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test06_synonymes/problem.hddl")
        plan = solver.solve()
        solver.output(plan)
        self.assertEqual(8, len(plan.get_progress_tracker().actions_taken))
        for i in range(4):
            self.assertEqual(domain.actions['noop1'], plan.get_progress_tracker().actions_taken[i * 2].mod)
            self.assertEqual(domain.actions['noop2'], plan.get_progress_tracker().actions_taken[(i * 2) + 1].mod)

    def test_7_arguments(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test07_arguments/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test07_arguments/problem.hddl")

        self.assertEqual(2, len(domain.actions['noop'].parameters))
        for p in domain.actions['noop'].parameters:
            self.assertEqual(domain.types['a'], p.type)

        plan = solver.solve()
        solver.output(plan)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))
        self.assertEqual(domain.actions['noop'], plan.get_progress_tracker().actions_taken[0].mod)
        self.assertEqual(2, len(plan.get_progress_tracker().actions_taken[0].parameters_used))
        self.assertEqual(problem.objects['b'], plan.get_progress_tracker().actions_taken[0].parameters_used['?a'])
        self.assertEqual(problem.objects['b'], plan.get_progress_tracker().actions_taken[0].parameters_used['?b'])

    def test_satellite01(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "satellite01/domain2.hddl")
        parser.parse_problem(self.IPC_Tests_path + "satellite01/1obs-1sat-1mod.hddl")
        plan = solver.solve()
        solver.output(plan)

        self.assertNotEqual(None, plan)
        self.assertEqual(5, len(plan.get_progress_tracker().actions_taken))

        self.assertEqual(domain.actions['switch_on'], plan.get_progress_tracker().actions_taken[0].mod)
        self.assertEqual(2, len(plan.get_progress_tracker().actions_taken[0].parameters_used))
        self.assertEqual(problem.objects['instrument0'], plan.get_progress_tracker().actions_taken[0].parameters_used['?so_i'])
        self.assertEqual(problem.objects['satellite0'], plan.get_progress_tracker().actions_taken[0].parameters_used['?so_s'])

        self.assertEqual(domain.actions['turn_to'], plan.get_progress_tracker().actions_taken[1].mod)
        self.assertEqual(3, len(plan.get_progress_tracker().actions_taken[1].parameters_used))
        self.assertEqual(problem.objects['groundstation2'], plan.get_progress_tracker().actions_taken[1].parameters_used['?t_d_new'])
        self.assertEqual(problem.objects['satellite0'], plan.get_progress_tracker().actions_taken[1].parameters_used['?t_s'])
        self.assertEqual(problem.objects['phenomenon6'], plan.get_progress_tracker().actions_taken[1].parameters_used['?t_d_prev'])

        self.assertEqual(domain.actions['calibrate'], plan.get_progress_tracker().actions_taken[2].mod)
        self.assertEqual(3, len(plan.get_progress_tracker().actions_taken[2].parameters_used))
        self.assertEqual(problem.objects['groundstation2'], plan.get_progress_tracker().actions_taken[2].parameters_used['?c_d'])
        self.assertEqual(problem.objects['satellite0'], plan.get_progress_tracker().actions_taken[2].parameters_used['?c_s'])
        self.assertEqual(problem.objects['instrument0'], plan.get_progress_tracker().actions_taken[2].parameters_used['?c_i'])

        self.assertEqual(domain.actions['turn_to'], plan.get_progress_tracker().actions_taken[3].mod)
        self.assertEqual(3, len(plan.get_progress_tracker().actions_taken[3].parameters_used))
        self.assertEqual(problem.objects['groundstation2'], plan.get_progress_tracker().actions_taken[3].parameters_used['?t_d_prev'])
        self.assertEqual(problem.objects['satellite0'], plan.get_progress_tracker().actions_taken[3].parameters_used['?t_s'])
        self.assertEqual(problem.objects['phenomenon4'], plan.get_progress_tracker().actions_taken[3].parameters_used['?t_d_new'])

        self.assertEqual(domain.actions['take_image'], plan.get_progress_tracker().actions_taken[4].mod)
        self.assertEqual(4, len(plan.get_progress_tracker().actions_taken[4].parameters_used))
        self.assertEqual(problem.objects['instrument0'], plan.get_progress_tracker().actions_taken[4].parameters_used['?ti_i'])
        self.assertEqual(problem.objects['satellite0'], plan.get_progress_tracker().actions_taken[4].parameters_used['?ti_s'])
        self.assertEqual(problem.objects['phenomenon4'], plan.get_progress_tracker().actions_taken[4].parameters_used['?ti_d'])
        self.assertEqual(problem.objects['thermograph0'], plan.get_progress_tracker().actions_taken[4].parameters_used['?ti_m'])

    @unittest.skip
    def test_transport01(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "transport01/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "transport01/pfile01.hddl")
        solver.set_heuristic(HammingDistance)

        # I think this one is not solvable
        plan = solver.solve()
        solver.output(plan)
        self.assertNotEqual(None, plan)

    # @unittest.skip
    def test_um_translog01(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "um-translog01/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "um-translog01/problem.hddl")
        plan = solver.solve()
        solver.output(plan)

        self.assertNotEqual(None, plan)
        self.assertNotEqual(0, len(plan.get_progress_tracker().actions_taken))
