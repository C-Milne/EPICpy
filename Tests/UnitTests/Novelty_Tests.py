import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Internal_Representation.state_novelty import StateNovelty
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver


class NoveltyTests(unittest.TestCase):
    def setUp(self):
        self.rover_path = "../Examples/Rover/"

    def test_novelty_state_add_element(self):
        # Check for example when true should be returned
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")

        state = StateNovelty()
        pred1 = ProblemPredicate(domain.get_predicate('at'), [problem.get_object('rover0'), problem.get_object('waypoint0')])
        state.add_element(pred1)

        pred2 = ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint0')])
        state.add_element(pred2)

        pred3 = ProblemPredicate(domain.get_predicate('can_traverse'), [problem.get_object('rover0'), problem.get_object('waypoint0'), problem.get_object('waypoint1')])
        state.add_element(pred3)

        pred4 = ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint3')])
        res = state.add_element(pred4)
        self.assertEqual(True, res)

    def test_novelty_state_add_element_1(self):
        # Check for example when false should be returned
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")

        state = StateNovelty()
        pred1 = ProblemPredicate(domain.get_predicate('at'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0')])
        state.add_element(pred1)

        pred2 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint0')])
        state.add_element(pred2)

        pred3 = ProblemPredicate(domain.get_predicate('can_traverse'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0'),
                                  problem.get_object('waypoint1')])
        state.add_element(pred3)

        pred4 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint0')])
        res = state.add_element(pred4)
        self.assertEqual(False, res)

    def test_novelty_state_add_element_2(self):
        # Check for example when false should be returned, but remove predicate before adding it again
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")

        state = StateNovelty()
        pred1 = ProblemPredicate(domain.get_predicate('at'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0')])
        state.add_element(pred1)

        pred2 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint0')])
        state.add_element(pred2)

        pred3 = ProblemPredicate(domain.get_predicate('can_traverse'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0'),
                                  problem.get_object('waypoint1')])
        state.add_element(pred3)

        state.remove_element(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint0')])

        pred4 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint0')])
        res = state.add_element(pred4)
        self.assertEqual(False, res)

    def test_novelty_state_add_element_3(self):
        # Check for example when true should be returned, but remove predicate before adding it again
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")

        state = StateNovelty()
        pred1 = ProblemPredicate(domain.get_predicate('at'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0')])
        state.add_element(pred1)

        pred2 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint0')])
        state.add_element(pred2)

        pred3 = ProblemPredicate(domain.get_predicate('can_traverse'),
                                 [problem.get_object('rover0'), problem.get_object('waypoint0'),
                                  problem.get_object('waypoint1')])
        state.add_element(pred3)

        state.remove_element(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint0')])

        pred4 = ProblemPredicate(domain.get_predicate('visible_from'),
                                 [problem.get_object('objective0'), problem.get_object('waypoint1')])
        state.add_element(pred4)
        res = state.add_element(pred3)
        self.assertEqual(True, res)

    def test_novelty_rover(self):
        domain, problem, parser, solver = env_setup(True, solver=1)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_novelty_no_reset_rover(self):
        domain, problem, parser, solver = env_setup(True, solver=2)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        res = solver.solve()
        self.assertNotEqual(None, res)
