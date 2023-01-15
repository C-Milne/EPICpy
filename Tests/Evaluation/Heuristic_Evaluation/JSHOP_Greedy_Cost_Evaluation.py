import unittest
from heuristic_evaluation import *
import os
import sys

try:
    from Solver.Search_Queues.Greedy_Cost_So_Far_Search_Queue import GreedyCostSearchQueue
except:
    original_cwd = os.getcwd()
    os.chdir("../../..")
    sys.path.insert(1, os.getcwd())
    from Solver.Search_Queues.Greedy_Cost_So_Far_Search_Queue import GreedyCostSearchQueue
    os.chdir(original_cwd)


class JSHOPGreedyCostEvaluation(unittest.TestCase):

    @unittest.skip
    def test_00_Basic_Solving_Time_HDDL_JSHOP(self):
        tests = [("../../../../Examples/Basic/basic.hddl", "../../../../Examples/Basic/pb1.hddl")]
        strats = [Strat("Breadth_First_HDDL", NoPruning)]
        run_tests(tests, strats, "Basic", False, SearchQueue=GreedyCostSearchQueue)

        tests = [("../../../../Examples/JShop/basic/basic.jshop", "../../../../Examples/JShop/basic/problem.jshop")]
        strats = [Strat("Breadth_First_JSHOP_GCost", NoPruning)]
        run_tests(tests, strats, "Basic", False, SearchQueue=GreedyCostSearchQueue)

    @unittest.skip
    def test_01_Rover_Solve_Time_JSHOP_BF_No_Pruning(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
                 ]

        strats = [Strat("Breadth_First_GCost", NoPruning)]

        run_tests(tests, strats, "JSHOP_Rover", False)

    @unittest.skip
    def test_02_Rover_Solve_Time_JSHOP_BF(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Breadth_First_Pruning_GCost", Pruning)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GreedyCostSearchQueue)

    @unittest.skip
    def test_03_Rover_Solve_Time_JSHOP_Tree(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Tree_Distance_GCost", TreeDistance)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GreedyCostSearchQueue)

    # @unittest.skip
    def test_04_Rover_Solve_Time_JSHOP_Hamming(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
                 ]

        strats = [Strat("Hamming_Distance_GCost", HammingDistance)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GreedyCostSearchQueue)
