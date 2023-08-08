import unittest
from unittest import mock
from io import StringIO
from test_Runner import RunnerTests
from test_HDDL_Parser import HDDLParsingTests
from test_HDDL_Grounding import HDDLGroundingTests
from test_Solving import SolvingTests
from test_IPC import IPCTests
from test_JSHOP_Parser import JSHOPParsingTests
from test_JSHOP_Solving import JSHOPSolvingTests
from test_Parameter_Selection import ParameterSelectionTests
from test_Heuristic import HeuristicTests
from test_Partial_Order import PartialOrderTests
from test_Progress_Tracker import ProgressTrackerTests
from test_State import StateTests
from test_Novelty import NoveltyTests


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(RunnerTests))
    test_suite.addTest(unittest.makeSuite(HDDLParsingTests))
    test_suite.addTest(unittest.makeSuite(HDDLGroundingTests))
    test_suite.addTest(unittest.makeSuite(JSHOPParsingTests))
    test_suite.addTest(unittest.makeSuite(JSHOPSolvingTests))
    test_suite.addTest(unittest.makeSuite(SolvingTests))
    test_suite.addTest(unittest.makeSuite(IPCTests))
    test_suite.addTest(unittest.makeSuite(ParameterSelectionTests))
    test_suite.addTest(unittest.makeSuite(HeuristicTests))
    test_suite.addTest(unittest.makeSuite(PartialOrderTests))
    test_suite.addTest(unittest.makeSuite(ProgressTrackerTests))
    test_suite.addTest(unittest.makeSuite(NoveltyTests))
    return test_suite


if __name__ == "__main__":
    test_suite = suite()

    with mock.patch('sys.stdout', new=StringIO()) as std_out:
        runner = unittest.TextTestRunner()
        runner.run(test_suite)
