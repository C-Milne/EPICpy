import unittest
import sys
import os
from heuristic_evaluation import *

try:
    from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
except:
    original_cwd = os.getcwd()
    os.chdir("../../..")
    sys.path.insert(1, os.getcwd())
    from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
    os.chdir(original_cwd)


class GBFSEvaluation(unittest.TestCase):

    @unittest.skip
    def test_01_Rover_1_4_BF_No_Pruning(self):
        """Test Rover p01 -> p04 with breadth first search without pruning - DONE"""
        tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl")]

        strats = [Strat("Breadth_First_Operations_GBFS", NoPruning)]

        run_tests(tests, strats, "Rover", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_02_Rover_1_4_BF_Pruning(self):
        """Test Rover p01 -> p04 with breadth first search and pruning - DONE"""
        tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl")]
        strats = [Strat("Breadth_First_Operations_Pruning_GBFS", Pruning)]
        run_tests(tests, strats, "Rover", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_03_Rover_1_15_Tree(self):
        """Test rover p01 -> p03 with Tree Distance - DONE"""
        tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p05.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p06.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p07.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p08.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p09.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p10.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p11.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p12.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p13.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p14.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p15.hddl")
                 ]

        strats = [Strat("Tree_Distance_GBFS", TreeDistance)]

        run_tests(tests, strats, "Rover", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_04_Rover_1_3_Delete_Relaxed(self):
        """Test rover p01 -> p03 with Delete Relaxed - DONE"""
        tests = [
            ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
            ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
            ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl")
        ]

        strats = [Strat("Delete_Relaxed_GBFS", DeleteRelaxed)]

        run_tests(tests, strats, "Rover", SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_05_Rover_1_4_Hamming(self):
        """Test rover with Hamming Distance heuristic -> DONE"""
        tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl"),
                 ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl")]

        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]

        run_tests(tests, strats, "Rover", SearchQueue=GBFSSearchQueue)

    """###################################################################################################################"""

    @unittest.skip
    def test_06_translog_all(self):
        """Test translog1 -> DONE"""
        tests = [("../../../../Examples/IPC_Tests/um-translog01/domain.hddl",
                  "../../../../Examples//IPC_Tests/um-translog01/problem.hddl")]

        strats = [Strat("Breadth_First_Operations_GBFS", NoPruning),
                  Strat("Breadth_First_Operations_Pruning_GBFS", Pruning),
                  Strat("Hamming_Distance_GBFS", HammingDistance),
                  Strat("Tree_Distance_GBFS", TreeDistance)]
        run_tests(tests, strats, "translog", False, SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_07_translog_Hamming(self):
        """Test translog1 -> DONE"""
        tests = [("../../../../Examples/IPC_Tests/um-translog01/domain.hddl",
                  "../../../../Examples//IPC_Tests/um-translog01/problem.hddl")]

        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]
        run_tests(tests, strats, "translog", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_08_translog_delete_relaxed(self):
        """Test translog1 with delete relaxed -> DONE"""
        tests = [("../../../../Examples/IPC_Tests/um-translog01/domain.hddl",
                  "../../../../Examples//IPC_Tests/um-translog01/problem.hddl")]

        strats = [Strat("Delete_Relaxed_GBFS", DeleteRelaxed)]
        run_tests(tests, strats, "translog", False, SearchQueue=GBFSSearchQueue)

    """###################################################################################################################"""

    @unittest.skip
    def test_09_depots_BF_No_Pruning(self):
        """Test depot p1 -> p3 with breadth first operations (WITHOUT PRUNING) - DONE"""
        tests = [("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p01.hddl"),
                 ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p02.hddl")
            , ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p03.hddl")]

        strats = [Strat("Breadth_First_Operations_GBFS", NoPruning)]

        run_tests(tests, strats, "Depot", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_10_depots_BF_Pruning(self):
        """Test depot p1 -> p3 with breadth first operations - DONE"""
        tests = [("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p01.hddl"),
                 ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p02.hddl"),
                 ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p03.hddl")]

        strats = [Strat("Breadth_First_Operations_Pruning_GBFS", Pruning)]

        run_tests(tests, strats, "Depot", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_11_depots_delete_relaxed(self):
        """Test depot p1 -> p3 with Delete Relaxed"""
        tests = [("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p01.hddl")]
        # ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p02.hddl")]
        # ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p03.hddl")]

        strats = [Strat("Delete_Relaxed_GBFS", DeleteRelaxed)]

        run_tests(tests, strats, "Depot", SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_12_depots_hamming(self):
        """Test depot p1 -> p3 with Hamming Distance - DONE"""
        tests = [("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p01.hddl"),
                 ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p02.hddl"),
                 ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p03.hddl")]

        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]

        run_tests(tests, strats, "Depot", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_13_depots_tree(self):
        """Test depot p1 -> p3 with Tree Distance- DONE"""
        tests = [
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p01.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p02.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p03.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p04.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p05.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p06.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p07.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p08.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p09.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p10.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p11.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p12.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p13.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p14.hddl"),
                ("../../../../Examples/Depots/domain.hddl", "../../../../Examples/Depots/p15.hddl")
        ]

        strats = [Strat("Tree_Distance_GBFS", TreeDistance)]

        run_tests(tests, strats, "Depot", SearchQueue=GBFSSearchQueue)

    """###################################################################################################################"""

    @unittest.skip
    def test_14_barman_BF_No_Pruning(self):
        """Test Barman with breadth first (NO PRUNING) - DONE"""
        tests = [("../../../../Examples/Barman/domain.hddl", "../../../../Examples/Barman/pfile01.hddl")]
        strats = [Strat("Breadth_First_Operations_GBFS", NoPruning)]
        run_tests(tests, strats, "Barman", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_15_barman_BF_Pruning(self):
        """Test Barman with breadth first - DONE"""
        tests = [("../../../../Examples/Barman/domain.hddl", "../../../../Examples/Barman/pfile01.hddl")]
        strats = [Strat("Breadth_First_Operations_Pruning_GBFS", Pruning)]
        run_tests(tests, strats, "Barman", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_16_barman_delete_relaxed(self):
        """Test Barman with Delete Relaxed - DONE"""
        tests = [("../../../../Examples/Barman/domain.hddl", "../../../../Examples/Barman/pfile01.hddl")]
        strats = [Strat("Delete_Relaxed_GBFS", DeleteRelaxed)]
        run_tests(tests, strats, "Barman", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_17_barman_tree(self):
        """Test Barman with Tree Distance - DONE"""
        tests = [("../../../../Examples/Barman/domain.hddl", "../../../../Examples/Barman/pfile01.hddl")]
        strats = [Strat("Tree_Distance_GBFS", TreeDistance)]
        run_tests(tests, strats, "Barman", SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_18_barman_hamming(self):
        """Test Barman with Hamming Distance - DONE"""
        tests = [("../../../../Examples/Barman/domain.hddl", "../../../../Examples/Barman/pfile01.hddl")]
        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]
        run_tests(tests, strats, "Barman", SearchQueue=GBFSSearchQueue)

    """###################################################################################################################"""

    @unittest.skip
    def test_19_factories_BF_No_Pruning(self):
        """Test Factories with Breadth First (NO PRUNING) - DONE"""
        tests = [("../../../../Examples/Factories/domain.hddl", "../../../../Examples/Factories/pfile01.hddl")]
        strats = [Strat("Breadth_First_Operations_GBFS", NoPruning)]
        run_tests(tests, strats, "Factories", False, SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_20_factories_BF_Pruning(self):
        """Test factories with Breadth First - DONE"""
        tests = [("../../../../Examples/Factories/domain.hddl", "../../../../Examples/Factories/pfile01.hddl")]
        strats = [Strat("Breadth_First_Operations_Pruning_GBFS", Pruning)]
        run_tests(tests, strats, "Factories", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_21_factories_tree(self):
        """Test Factories with Tree Distance"""
        tests = [("../../../../Examples/Factories/domain.hddl", "../../../../Examples/Factories/pfile01.hddl")]
        strats = [Strat("Tree_Distance_GBFS", TreeDistance)]
        run_tests(tests, strats, "Factories", SearchQueue=GBFSSearchQueue)

    # @unittest.skip
    def test_22_factories_hamming(self):
        """Test Factories with Hamming Distance - DONE"""
        tests = [("../../../../Examples/Factories/domain.hddl", "../../../../Examples/Factories/pfile01.hddl")]
        strats = [Strat("Hamming_Distance_GBFS", HammingDistance)]
        run_tests(tests, strats, "Factories", SearchQueue=GBFSSearchQueue)

    @unittest.skip
    def test_23_factories_Delete_Relaxed(self):
        """Test Factories with Delete Relaxed"""
        tests = [("../../../../Examples/Factories/domain.hddl", "../../../../Examples/Factories/pfile01.hddl")]
        strats = [Strat("Delete_Relaxed_GBFS", DeleteRelaxed)]
        run_tests(tests, strats, "Factories", SearchQueue=GBFSSearchQueue)
