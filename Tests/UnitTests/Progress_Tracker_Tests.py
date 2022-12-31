import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker


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
        self.assertEqual(1, 2)
