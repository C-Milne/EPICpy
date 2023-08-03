import unittest
from unittest import mock
from io import StringIO
import os, sys

try:
    from Tests.UnitTests.Runner_Tests import RunnerTests
    from Tests.UnitTests.HDDL_Parser_Tests import HDDLParsingTests
    from Tests.UnitTests.HDDL_Grounding_Tests import HDDLGroundingTests
    from Tests.UnitTests.Solving_Tests import SolvingTests
    from Tests.UnitTests.IPC_Tests import IPCTests
    from Tests.UnitTests.JSHOP_Parser_Tests import JSHOPParsingTests
    from Tests.UnitTests.JSHOP_Solving_Tests import JSHOPSolvingTests
    from Tests.UnitTests.Parameter_Selection_Tests import ParameterSelectionTests
    from Tests.UnitTests.Heuristic_Tests import HeuristicTests
    from Tests.UnitTests.Partial_Order_Tests import PartialOrderTests
    from Tests.UnitTests.Progress_Tracker_Tests import ProgressTrackerTests
    from Tests.UnitTests.State_Tests import StateTests
    from Tests.UnitTests.Novelty_Tests import NoveltyTests
except:
    original_cwd = os.getcwd()
    os.chdir("../..")
    sys.path.insert(1, os.getcwd())
    os.chdir(original_cwd)
    from test_Runner import RunnerTests
    from test_HDDL_Parser import HDDLParsingTests
    # from Tests.UnitTests.HDDL_Grounding_Tests import HDDLGroundingTests
    # from Tests.UnitTests.Solving_Tests import SolvingTests
    # from Tests.UnitTests.IPC_Tests import IPCTests
    # from Tests.UnitTests.JSHOP_Parser_Tests import JSHOPParsingTests
    # from Tests.UnitTests.JSHOP_Solving_Tests import JSHOPSolvingTests
    # from Tests.UnitTests.Parameter_Selection_Tests import ParameterSelectionTests
    # from Tests.UnitTests.Heuristic_Tests import HeuristicTests
    # from Tests.UnitTests.Partial_Order_Tests import PartialOrderTests
    # from Tests.UnitTests.Progress_Tracker_Tests import ProgressTrackerTests
    # from Tests.UnitTests.State_Tests import StateTests
    # from Tests.UnitTests.Novelty_Tests import NoveltyTests

"""https://stackoverflow.com/questions/12011091/trying-to-implement-python-testsuite"""


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(RunnerTests))
    test_suite.addTest(unittest.makeSuite(HDDLParsingTests))
    # test_suite.addTest(unittest.makeSuite(HDDLGroundingTests))
    # test_suite.addTest(unittest.makeSuite(JSHOPParsingTests))
    # test_suite.addTest(unittest.makeSuite(JSHOPSolvingTests))
    # test_suite.addTest(unittest.makeSuite(SolvingTests))
    # test_suite.addTest(unittest.makeSuite(IPCTests))
    # test_suite.addTest(unittest.makeSuite(ParameterSelectionTests))
    # test_suite.addTest(unittest.makeSuite(HeuristicTests))
    # test_suite.addTest(unittest.makeSuite(PartialOrderTests))
    # test_suite.addTest(unittest.makeSuite(ProgressTrackerTests))
    # test_suite.addTest(unittest.makeSuite(NoveltyTests))
    return test_suite


if __name__ == "__main__":
    test_suite = suite()

    with mock.patch('sys.stdout', new=StringIO()) as std_out:
        runner = unittest.TextTestRunner()
        runner.run(test_suite)
