import unittest
from unittest import mock
from io import StringIO
import os
import sys

try:
    from Tests.Evaluation.Heuristic_Evaluation.hddl_searchQ_evaluation import HDDLSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.GBFS_Evaluation import GBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.Greedy_Cost_Evaluation import GreedyCostEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_searchQ_Evaluation import POSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_GBFS_Evaluation import POGBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_Greedy_Cost_Evaluation import POGreedyCostEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_SearchQ_Evaluation import JSHOPSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_GBFS_Evaluation import JSHOPGBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_Greedy_Cost_Evaluation import JSHOPGreedyCostEvaluation
except:
    original_cwd = os.getcwd()
    os.chdir("../../..")
    sys.path.insert(1, os.getcwd())
    os.chdir(original_cwd)
    from Tests.Evaluation.Heuristic_Evaluation.hddl_searchQ_evaluation import HDDLSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.GBFS_Evaluation import GBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.Greedy_Cost_Evaluation import GreedyCostEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_searchQ_Evaluation import POSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_GBFS_Evaluation import POGBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.PO_Greedy_Cost_Evaluation import POGreedyCostEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_SearchQ_Evaluation import JSHOPSearchQEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_GBFS_Evaluation import JSHOPGBFSEvaluation
    from Tests.Evaluation.Heuristic_Evaluation.JSHOP_Greedy_Cost_Evaluation import JSHOPGreedyCostEvaluation


"""https://stackoverflow.com/questions/12011091/trying-to-implement-python-testsuite"""


def suite():
    test_suite = unittest.TestSuite()
    # test_suite.addTest(unittest.makeSuite(HDDLSearchQEvaluation))
    # test_suite.addTest(unittest.makeSuite(GBFSEvaluation))
    # test_suite.addTest(unittest.makeSuite(GreedyCostEvaluation))
    # test_suite.addTest(unittest.makeSuite(POSearchQEvaluation))
    # test_suite.addTest(unittest.makeSuite(POGBFSEvaluation))
    # test_suite.addTest(unittest.makeSuite(POGreedyCostEvaluation))
    test_suite.addTest(unittest.makeSuite(JSHOPSearchQEvaluation))
    test_suite.addTest(unittest.makeSuite(JSHOPGBFSEvaluation))
    test_suite.addTest(unittest.makeSuite(JSHOPGreedyCostEvaluation))
    return test_suite


if __name__ == "__main__":
    test_suite = suite()

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
