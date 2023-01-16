import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Internal_Representation.state import State
from Internal_Representation.predicate import Predicate
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.Object import Object
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
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

    def test_final_state_rover1_ham_gbfs_duplicates(self):
        # Run the rover 1 problem and check for available predicates (rover1 should only occur once)
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_search_queue(GBFSSearchQueue)
        solver.set_heuristic(HammingDistancePartialOrder)

        res = solver.solve()
        self.assertEqual(1, len(res.current_state.get_indexes('available')))
