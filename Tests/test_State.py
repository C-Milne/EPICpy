import unittest
from TestTools.env_setup import env_setup
from Internal_Representation.state import State
from Internal_Representation.predicate import Predicate
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.Object import Object
from Internal_Representation.action import Action
from Internal_Representation.subtasks import Subtasks
from Internal_Representation.effects import Effects
from Internal_Representation.reg_parameter import RegParameter
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue


class StateTests(unittest.TestCase):

    def setUp(self) -> None:
        self.rover_path = "../Examples/Rover/"

    def test_add_same_predicate_to_state(self):
        state = State()
        predicate1 = Predicate('test-pred', [RegParameter('?a')])
        object1 = Object('ob1')
        prob_pred1 = ProblemPredicate(predicate1, [object1])
        prob_pred2 = ProblemPredicate(predicate1, [object1])

        state.add_element(prob_pred1)
        state.add_element(prob_pred2)

        self.assertEqual(1, len(state))
        self.assertEqual([prob_pred1], state.elements)
        self.assertEqual({'test-pred': [0]}, state._index)

    def test_add_same_predicate_to_state_2(self):
        state = State()
        predicate1 = Predicate('test-pred', [RegParameter('?a')])
        object1 = Object('ob1')
        prob_pred1 = ProblemPredicate(predicate1, [object1])
        prob_pred3 = ProblemPredicate(predicate1, [object1])
        object2 = Object('ob2')
        prob_pred2 = ProblemPredicate(predicate1, [object2])

        state.add_element(prob_pred1)
        state.add_element(prob_pred2)
        state.add_element(prob_pred3)

        self.assertEqual(2, len(state))
        self.assertEqual([prob_pred1, prob_pred2], state.elements)
        self.assertEqual({'test-pred': [0, 1]}, state._index)

    def test_final_state_rover1_ham_gbfs_duplicates(self):
        # Run the rover 1 problem and check for available predicates (rover1 should only occur once)
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_search_queue(GBFSSearchQueue)
        solver.set_heuristic(HammingDistancePartialOrder)

        res = solver.solve()
        self.assertEqual(1, len(res.current_state.get_indexes('available')))

    def test_expanding_action_which_adds_and_removes_same_predicate(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain('TestTools/state_testing/domain1.hddl')
        parser.parse_problem('TestTools/state_testing/problem1.hddl')
        solver.set_search_queue(GBFSSearchQueue)
        solver.set_heuristic(TreeDistance)
        solver.solve(search=False)
        res = solver._search(True)
        self.assertNotEqual(None, res)
        res_state = res.current_state
        self.assertIsNotNone(res_state.get_indexes('shakerLevel'))
        self.assertEqual(1, len(res_state.get_indexes('shakerLevel')))
        self.assertIn(ProblemPredicate(domain.get_predicate('shakerLevel'), [problem.get_object('shaker1'), problem.get_object('level1')]), res_state.elements)

    def test_hashing_frozenset_state(self):
        predicate1 = Predicate('test-pred', [RegParameter('?a')])
        predicate2 = Predicate('test-pred-b', [RegParameter('?a')])
        object1 = Object('ob1')
        object2 = Object('ob2')

        state1 = State()
        prob_pred1 = ProblemPredicate(predicate1, [object1])
        prob_pred2 = ProblemPredicate(predicate1, [object2])
        prob_pred3 = ProblemPredicate(predicate2, [object1])
        state1.add_element(prob_pred1)
        state1.add_element(prob_pred2)
        state1.add_element(prob_pred3)

        state2 = State()
        prob_pred2_1 = ProblemPredicate(predicate1, [object1])
        prob_pred2_2 = ProblemPredicate(predicate1, [object2])
        prob_pred2_3 = ProblemPredicate(predicate2, [object1])

        state2.add_element(prob_pred2_3)
        state2.add_element(prob_pred2_1)
        state2.add_element(prob_pred2_2)

        state1_hash = hash(frozenset(state1.elements))
        state2_hash = hash(frozenset(state2.elements))
        self.assertEqual(state1_hash, state2_hash)

    def test_hashing_frozenset_state_1(self):
        predicate1 = Predicate('test-pred', [RegParameter('?a')])
        predicate2 = Predicate('test-pred-b', [RegParameter('?a')])
        object1 = Object('ob1')
        object2 = Object('ob2')

        state1 = State()
        prob_pred1 = ProblemPredicate(predicate1, [object1])
        prob_pred2 = ProblemPredicate(predicate1, [object2])
        prob_pred3 = ProblemPredicate(predicate2, [object1])
        state1.add_element(prob_pred1)
        state1.add_element(prob_pred2)
        state1.add_element(prob_pred3)

        state2 = State()
        prob_pred2_1 = ProblemPredicate(predicate1, [object1])
        prob_pred2_2 = ProblemPredicate(predicate1, [object2])
        prob_pred2_3 = ProblemPredicate(predicate2, [object1])
        prob_pred2_4 = ProblemPredicate(predicate2, [object2])

        state2.add_element(prob_pred2_3)
        state2.add_element(prob_pred2_4)
        state2.add_element(prob_pred2_1)
        state2.add_element(prob_pred2_2)

        state1_hash = hash(frozenset(state1.elements))
        state2_hash = hash(frozenset(state2.elements))
        self.assertNotEqual(state1_hash, state2_hash)

    def test_hashing_frozenset_state_2(self):
        predicate1 = Predicate('test-pred', [RegParameter('?a')])
        predicate2 = Predicate('test-pred-b', [RegParameter('?a')])
        predicate3 = Predicate('test-pred-c', [RegParameter('?a')])
        object1 = Object('ob1')
        object2 = Object('ob2')

        state1 = State()
        prob_pred1 = ProblemPredicate(predicate1, [object1])
        prob_pred2 = ProblemPredicate(predicate1, [object2])
        prob_pred3 = ProblemPredicate(predicate2, [object1])
        prob_pred4 = ProblemPredicate(predicate3, [object2])
        state1.add_element(prob_pred1)
        state1.add_element(prob_pred2)
        state1.add_element(prob_pred3)
        state1.add_element(prob_pred4)

        state2 = State()
        prob_pred2_1 = ProblemPredicate(predicate1, [object1])
        prob_pred2_2 = ProblemPredicate(predicate1, [object2])
        prob_pred2_3 = ProblemPredicate(predicate2, [object1])
        prob_pred2_4 = ProblemPredicate(predicate2, [object2])

        state2.add_element(prob_pred2_3)
        state2.add_element(prob_pred2_4)
        state2.add_element(prob_pred2_1)
        state2.add_element(prob_pred2_2)

        state1_hash = hash(frozenset(state1.elements))
        state2_hash = hash(frozenset(state2.elements))
        self.assertNotEqual(state1_hash, state2_hash)

    # def test_expanding_action_which_adds_and_removes_same_predicate(self):
    #     domain, problem, parser, solver = env_setup(True, True)
    #
    #     state = State()
    #     predicate1 = Predicate('test-pred', [RegParameter('?a')])
    #     object1 = Object('ob1')
    #     prob_pred1 = ProblemPredicate(predicate1, [object1])
    #     object2 = Object('ob2')
    #     prob_pred2 = ProblemPredicate(predicate1, [object2])
    #
    #     state.add_element(prob_pred1)
    #     state.add_element(prob_pred2)
    #
    #     action_effects = Effects()
    #     action_effects.add_effect(predicate1, ['?a'], True)
    #     action = Action('action1', [RegParameter('?a')], None, action_effects)
    #     subtask = Subtasks(True)
    #     subtask.add_subtask('1', action, [object1])
    #
    #     print('here')
    #     # solver._expand_action(subtask.)
    #
    #     self.assertEqual(2, len(state))
    #     self.assertEqual([prob_pred1, prob_pred2], state.elements)
    #     self.assertEqual({'test-pred': [0, 1]}, state._index)
