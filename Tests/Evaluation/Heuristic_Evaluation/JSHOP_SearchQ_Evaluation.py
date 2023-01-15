import unittest
from heuristic_evaluation import *


class JSHOPSearchQEvaluation(unittest.TestCase):

    @unittest.skip
    def test_00_Basic_Parsing_Time_HDDL_JSHOP(self):
        tests = [("../../../../Examples/Basic/basic.hddl", "../../../../Examples/Basic/pb1.hddl")]
        strats = [Strat("HDDL_Parsing", NoPruning)]
        run_tests(tests, strats, "Basic", True, search=False)

        tests = [("../../../../Examples/JShop/basic/basic.jshop", "../../../../Examples/JShop/basic/problem.jshop")]
        strats = [Strat("JSHOP_Parsing", NoPruning)]
        run_tests(tests, strats, "Basic", False, search=False)

    @unittest.skip
    def test_01_Basic_Solving_Time_HDDL_JSHOP(self):
        tests = [("../../../../Examples/Basic/basic.hddl", "../../../../Examples/Basic/pb1.hddl")]
        strats = [Strat("Breadth_First_HDDL", NoPruning)]
        run_tests(tests, strats, "Basic", False)

        tests = [("../../../../Examples/JShop/basic/basic.jshop", "../../../../Examples/JShop/basic/problem.jshop")]
        strats = [Strat("Breadth_First_JSHOP", NoPruning)]
        run_tests(tests, strats, "Basic", False)

    @unittest.skip
    def test_02_Rover_Parsing_Time_HDDL(self):
        tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl")
            , ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl")
            , ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl")
            , ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl")
            , ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p05.hddl")
                 ]

        strats = [Strat("Breadth_First_HDDL", NoPruning)]

        run_tests(tests, strats, "HDDL_JSHOP_Rover", True, search=False)

    @unittest.skip
    def test_03_Rover_Parsing_Time_JSHOP(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb5.jshop")
                 ]

        strats = [Strat("Breadth_First_JSHOP", NoPruning)]

        run_tests(tests, strats, "HDDL_JSHOP_Rover", False, search=False)

    @unittest.skip
    def test_04_Rover_Solve_Time_JSHOP_BF_No_Pruning(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
                 ]

        strats = [Strat("Breadth_First", NoPruning)]

        run_tests(tests, strats, "JSHOP_Rover", True)

    @unittest.skip
    def test_05_Rover_Solve_Time_JSHOP_BF(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Breadth_First_Pruning", Pruning)]

        run_tests(tests, strats, "JSHOP_Rover")

    @unittest.skip
    def test_06_Rover_Solve_Time_JSHOP_Tree(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb4.jshop")
                 ]

        strats = [Strat("Tree_Distance", TreeDistance)]

        run_tests(tests, strats, "JSHOP_Rover")

    # @unittest.skip
    def test_07_Rover_Solve_Time_JSHOP_Hamming(self):
        tests = [("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb1.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb2.jshop")
            , ("../../../../Examples/JShop/rover/rover.jshop", "../../../../Examples/JShop/rover/pb3.jshop")
                 ]

        strats = [Strat("Hamming_Distance", HammingDistance)]

        run_tests(tests, strats, "JSHOP_Rover")
