import unittest
from heuristic_evaluation import *
import os
import sys

try:
    from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
except:
    original_cwd = os.getcwd()
    os.chdir("../../..")
    sys.path.insert(1, os.getcwd())
    from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
    os.chdir(original_cwd)


class JSHOPGBFSEvaluation(unittest.TestCase):

    @unittest.skip
    def test_01_Basic_Solving_Time_HDDL_JSHOP(self):
        tests = [("../../../../Examples/Basic/basic.hddl", "../../../../Examples/Basic/pb1.hddl")]
        strats = [Strat("Breadth_First_HDDL", NoPruning)]
        run_tests(tests, strats, "Basic", False, SearchQueue=GBFSSearchQueue)

        tests = [("../../../../Examples/JShop/basic/basic.jshop", "../../../../Examples/JShop/basic/problem.jshop")]
        strats = [Strat("Breadth_First_JSHOP_GBFS", NoPruning)]
        run_tests(tests, strats, "Basic", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_02_Rover_Solve_Time_JSHOP_BF_No_Pruning(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
                 ]

        strats = [Strat("Breadth_First_GBFS", NoPruning)]

        run_tests(tests, strats, "JSHOP_Rover", False)

    @unittest.skip
    def test_03_Rover_Solve_Time_JSHOP_BF(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Breadth_First_Pruning_GBFS", Pruning)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_04_Rover_Solve_Time_JSHOP_Tree(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Tree_Distance_GBFS", TreeDistance)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_05_Rover_Solve_Time_JSHOP_Hamming(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
                 ]

        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]

        run_tests(tests, strats, "JSHOP_Rover", SearchQueue=GBFSSearchQueue)
