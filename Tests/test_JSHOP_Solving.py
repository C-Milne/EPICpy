import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from queue import PriorityQueue
from Tests.TestTools.env_setup import env_setup
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Progress_Tracking.action_tracker import ActionTracker


class JSHOPSolvingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.basic_path = "Examples/JShop/basic/"
        self.block_path = "Examples/JShop/blocks/"
        # self.block_path = "Tests/Examples/JShop/blocks/"
        self.forall_test_path = "Examples/JShop/foralltest/"
        self.forall_path = "Examples/JShop/forall/"
        self.rover_test_path = "Tests/TestTools/J-Rover/"

    @unittest.skip
    def test_derived_predicate_processing_1(self):
        """This test takes ages to process. For one of the derived predicates there is 84100 parameter options"""
        # Test 'same' axiom from blocks domain
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.block_path + "blocks")
        parser.parse_problem(self.block_path + "problem")
        solver.solve(search=False)

        model = solver.search_models._Q.pop(0)

        solver.compute_derived_predicates(model)
        self.assertEqual(1, 2)

    def test_forall_1(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_test_path + "forall.jshop")
        parser.parse_problem(self.forall_test_path + "problem.jshop")
        solver.solve(search=False)

        self.assertEqual(['forall', ['?v'], [['p', '?v']], [['q', '?v'], ['q', '?v'], ['not', ['w', '?v']]]],
                         domain.methods['method0'].preconditions.conditions)

        model = solver.search_models._Q.get()
        res = domain.methods['method0'].preconditions.evaluate({}, model, problem)

        # Test Running this example
        self.assertEqual(False, res)

    def test_forall_satisfier_selection(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_test_path + "forall.jshop")
        parser.parse_problem(self.forall_test_path + "problem.jshop")
        solver.solve(search=False)

        model = solver.search_models._Q.get()

        method = domain.methods['method0']
        cons = method.preconditions.head
        satisfying_obs = cons._collect_objects({}, model, problem)
        self.assertEqual(1, len(satisfying_obs))
        self.assertEqual('y', satisfying_obs[0].name)
        self.assertEqual(problem.objects['y'], satisfying_obs[0])

    def test_forall_2(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_path + "forall.jshop")
        parser.parse_problem(self.forall_path + "problem.jshop")
        solver.solve(search=False)

        solver.parameter_selector.presolving_processing(domain, problem)

        model = solver.search_models._Q.get()

        # Test applying forall effect method
        self.assertIn(ProblemPredicate(domain.predicates['in'], [problem.objects['p3'], problem.objects['t2']]),
                      model.current_state.elements)

        subT = model.search_modifiers.pop(0)
        solver._expand_task(subT, model)

        model = solver.search_models._Q.get()
        subT = model.search_modifiers.pop(0)
        solver._expand_method(subT, model)

        model = solver.search_models._Q.get()
        subT = model.search_modifiers.pop(0)
        solver._expand_task(subT, model)

        search_models = solver.search_models._Q
        self.assertEqual(2, len(search_models.queue))

        model = search_models.queue[0]
        self.assertEqual(2, len(model.search_modifiers))
        mod = model.search_modifiers[0]
        self.assertEqual(domain.methods['method2'], mod.task)
        self.assertEqual({'?x': problem.objects['city2'], '?t': problem.objects['t2'], '?z': problem.objects['p1']}, mod.given_params)

        mod = model.search_modifiers[1]
        self.assertEqual(domain.actions['!drive'], mod.task)
        self.assertEqual({'?x': problem.objects['city2'], '?y': problem.objects['city1'], '?t': problem.objects['t2']},
                         mod.given_params)

        model = search_models.queue[1]
        self.assertEqual(2, len(model.search_modifiers))
        mod = model.search_modifiers[0]
        self.assertEqual(domain.methods['method2'], mod.task)
        self.assertEqual({'?x': problem.objects['city2'], '?t': problem.objects['t2'], '?z': problem.objects['p4']},
                         mod.given_params)

        mod = model.search_modifiers[1]
        self.assertEqual(domain.actions['!drive'], mod.task)
        self.assertEqual({'?x': problem.objects['city2'], '?y': problem.objects['city1'], '?t': problem.objects['t2']},
                         mod.given_params)

    def test_forall_example_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_path + "forall.jshop")
        parser.parse_problem(self.forall_path + "problem.jshop")
        res = solver.solve()

        self.assertNotEqual(None, res)
        self.assertIn(ActionTracker(domain.actions['!load'], {'?z': problem.objects['p1'], '?t': problem.objects['t2']}),
                      res.get_progress_tracker().actions_taken)
        self.assertIn(
            ActionTracker(domain.actions['!load'], {'?z': problem.objects['p4'], '?t': problem.objects['t2']}),
            res.get_progress_tracker().actions_taken)
        self.assertIn(
            ActionTracker(domain.actions['!drive'], {'?t': problem.objects['t2'], '?x': problem.objects['city2'],
                                                     '?y': problem.objects['city1']}), res.get_progress_tracker().actions_taken)
        self.assertIn(ProblemPredicate(domain.predicates['at'], [problem.objects['p1'], problem.objects['city1']]),
                      res.current_state.elements)
        self.assertIn(ProblemPredicate(domain.predicates['at'], [problem.objects['p3'], problem.objects['city1']]),
                      res.current_state.elements)
        self.assertIn(ProblemPredicate(domain.predicates['at'], [problem.objects['p4'], problem.objects['city1']]),
                      res.current_state.elements)
        self.assertIn(ProblemPredicate(domain.predicates['at'], [problem.objects['p2'], problem.objects['city1']]),
                      res.current_state.elements)

    @unittest.skip
    def test_forall_example_execution_2(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_test_path + "forall")
        parser.parse_problem(self.forall_test_path + "problem")
        res = solver.solve()

        self.assertEqual(1, 2)

    def test_basic_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.basic_path + "basic.jshop")
        parser.parse_problem(self.basic_path + "problem.jshop")
        res = solver.solve()

        self.assertNotEqual(None, res)
        self.assertIn(ActionTracker(domain.actions['!drop'], {'?a': problem.objects['kiwi']}), res.get_progress_tracker().actions_taken)
        self.assertIn(ActionTracker(domain.actions['!pickup'], {'?a': problem.objects['banjo']}), res.get_progress_tracker().actions_taken)

    def test_rover_execution_part_guided(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_test_path + "rover.jshop")
        parser.parse_problem(self.rover_test_path + "problem.jshop")

        solver.solve(search=False)
        solver.parameter_selector.presolving_processing(domain, problem)
        # res = solver.solve()

        solver._search(True)
        solver._search(True)
        solver._search(True)
        model_to_add = solver.search_models._Q.queue[0]
        solver.search_models._Q = PriorityQueue()
        solver.search_models._Q.put(model_to_add)
        solver.search_models._Q.queue[0].search_modifiers[0].given_params['?to'] = problem.objects['waypoint5']
        search_models = solver.search_models._Q
        solver._search(True)
        solver._search(True)
        solver._search(True)
        res = solver._search()
        # solver._search(True)
        # solver._search(True)
        search_models = solver.search_models._Q
        self.assertNotEqual(None, res)
        # solver.output(res)

    def test_rover_execution(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_test_path + "rover.jshop")
        parser.parse_problem(self.rover_test_path + "problem.jshop")

        solver.solve(search=False)
        solver.parameter_selector.presolving_processing(domain, problem)
        res = solver.solve()
        search_models = solver.search_models._Q
        self.assertNotEqual(None, res)
        # solver.output(res)

    @unittest.skip
    def test_evaluating_goal_precondition(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.block_path + "blocks")
        parser.parse_problem(self.block_path + "problem")
        self.assertEqual(1, 2)
