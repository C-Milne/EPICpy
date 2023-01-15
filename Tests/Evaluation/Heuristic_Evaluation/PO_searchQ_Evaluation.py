import unittest
from heuristic_evaluation import *

class POSearchQEvaluation(unittest.TestCase):

    @unittest.skip
    def test_00_PO_Rover_Breadth_First_No_Pruning(self):
        """Test PO-Rover Breadth First (NO PRUNING) - DONE"""
        tests = [("../../../../Examples/Partial_Order/Rover/domain.hddl", "../../../../Examples/Partial_Order/Rover/pfile01.hddl"),
        ("../../../../Examples/Partial_Order/Rover/domain.hddl", "../../../../Examples/Partial_Order/Rover/pfile02.hddl"),
        ("../../../../Examples/Partial_Order/Rover/domain.hddl", "../../../../Examples/Partial_Order/Rover/pfile03.hddl"),
        ("../../../../Examples/Partial_Order/Rover/domain.hddl", "../../../../Examples/Partial_Order/Rover/pfile04.hddl")]

        strats = [Strat("Breadth_First_Operations", NoPruning)]
        run_tests(tests, strats, "Rover_Partial_Order", True, partial_order=True)

    @unittest.skip
    def test_01_PO_Rover_Breadth_First(self):
        """Test PO-Rover Breadth First - DONE"""
        tests = [("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile01.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile02.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile03.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile04.hddl")]

        strats = [Strat("Breadth_First_Operations_PO_Pruning", PartialOrderPruning)]
        run_tests(tests, strats, "Rover_Partial_Order", partial_order=True)

    # @unittest.skip
    def test_02_PO_Rover_Hamming(self):
        """Test Hamming Distance (Partial Order) - DONE"""
        tests = [("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile01.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile02.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile03.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile04.hddl")]

        strats = [Strat("Hamming_Distance_Partial_Order", HammingDistancePartialOrder)]
        run_tests(tests, strats, "Rover_Partial_Order", partial_order=True)

    @unittest.skip
    def test_03_PO_Rover_Tree(self):
        """Test Tree Distance (Partial Order)"""
        tests = [("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile01.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile02.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile03.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile04.hddl")]

        strats = [Strat("Tree_Distance_Partial_Order", TreeDistancePartialOrder)]
        run_tests(tests, strats, "Rover_Partial_Order", partial_order=True)

    @unittest.skip
    def test_04_PO_Rover_Delete_Relaxed(self):
        """Test Tree Distance (Partial Order)"""
        tests = [("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile01.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile02.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile03.hddl"),
                 ("../../../../Examples/Partial_Order/Rover/domain.hddl",
                  "../../../../Examples/Partial_Order/Rover/pfile04.hddl")]

        strats = [Strat("Delete_Relaxed_Partial_Order", DeleteRelaxedPartialOrder)]
        run_tests(tests, strats, "Rover_Partial_Order", partial_order=True)

    """###################################################################################################################"""

    @unittest.skip
    def test_05_PO_Barman_Breadth_First_No_Pruning(self):
        """Test Barman Partial Order - Breadth First (No Pruning) -> DONE"""
        tests = [("../../../../Examples/Partial_Order/Barman/domain.hddl",
                  "../../../../Examples/Partial_Order/Barman/pfile01.hddl")
                 # ,("../../../../Examples/Partial_Order/Barman/domain.hddl", "../../../../Examples/Partial_Order/Barman/pfile02.hddl")
                 ]
        strats = [Strat("Breadth_First_Operations", NoPruning)]
        run_tests(tests, strats, "Barman_Partial_Order", True, partial_order=True)

    @unittest.skip
    def test_06_PO_Barman_Breadth_First(self):
        """Test Barman Partial Order - Breadth First-> DONE"""
        tests = [("../../../../Examples/Partial_Order/Barman/domain.hddl",
                  "../../../../Examples/Partial_Order/Barman/pfile01.hddl")
                 # ,("../../../../Examples/Partial_Order/Barman/domain.hddl", "../../../../Examples/Partial_Order/Barman/pfile02.hddl")
                 ]
        strats = [Strat("Breadth_First_Operations_PO_Pruning", PartialOrderPruning)]
        run_tests(tests, strats, "Barman_Partial_Order", partial_order=True)

    # @unittest.skip
    def test_07_PO_Barman_Hamming(self):
        """Test Barman Partial Order - Hamming Distance -> DONE"""
        tests = [("../../../../Examples/Partial_Order/Barman/domain.hddl",
                  "../../../../Examples/Partial_Order/Barman/pfile01.hddl")
                 # ,("../../../../Examples/Partial_Order/Barman/domain.hddl", "../../../../Examples/Partial_Order/Barman/pfile02.hddl")
                 ]
        strats = [Strat("Hamming_Distance_Partial_Order", HammingDistancePartialOrder)]
        run_tests(tests, strats, "Barman_Partial_Order", partial_order=True)

    @unittest.skip
    def test_08_PO_Barman_Tree(self):
        """Test Barman Partial Order - Tree Distance -> DONE"""
        tests = [("../../../../Examples/Partial_Order/Barman/domain.hddl",
                  "../../../../Examples/Partial_Order/Barman/pfile01.hddl")
                 # ,("../../../../Examples/Partial_Order/Barman/domain.hddl", "../../../../Examples/Partial_Order/Barman/pfile02.hddl")
                 ]
        strats = [Strat("Tree_Distance_Partial_Order", TreeDistancePartialOrder)]
        run_tests(tests, strats, "Barman_Partial_Order", partial_order=True)

    @unittest.skip
    def test_09_PO_Barman_Delete_Relaxed(self):
        """Test Barman Partial Order - Tree Distance -> DONE"""
        tests = [("../../../../Examples/Partial_Order/Barman/domain.hddl",
                  "../../../../Examples/Partial_Order/Barman/pfile01.hddl")
                 # ,("../../../../Examples/Partial_Order/Barman/domain.hddl", "../../../../Examples/Partial_Order/Barman/pfile02.hddl")
                 ]
        strats = [Strat("Delete_Relaxed_Partial_Order", DeleteRelaxedPartialOrder)]
        run_tests(tests, strats, "Barman_Partial_Order", partial_order=True)
