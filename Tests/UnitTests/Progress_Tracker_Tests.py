import os.path
import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from runner import Runner


class ProgressTrackerTests(unittest.TestCase):

    def setUp(self):
        self.basic_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"

    def test_basic_pandaverify_output(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.basic_path)
        parser.parse_problem(self.basic_pb1_path)
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
2 drop kiwi
3 pickup banjo
root 0
0 swap banjo kiwi -> have_second 2 3
<==""", str(res.progress_tracker))

    def test_basic_pandaverify_output_file(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.basic_path)
        parser.parse_problem(self.basic_pb1_path)
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        Runner.output_result_file(res, "basic_test_panda.txt")

        # Check output file exists
        self.assertEqual(True, os.path.isfile('output/basic_test_panda.txt'))

        # Check contents of output file
        with open('output/basic_test_panda.txt') as f:
            file_contents = f.read()

        self.assertEqual("""==>
2 drop kiwi
3 pickup banjo
root 0
0 swap banjo kiwi -> have_second 2 3
<==""", file_contents)
