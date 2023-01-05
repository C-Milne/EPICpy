import os.path
import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from runner import Runner


class ProgressTrackerTests(unittest.TestCase):

    def setUp(self):
        self.basic_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"
        self.rover_path = "../Examples/Rover/"

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

    def test_rover_1_pandaverify_output(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.rover_path + 'domain.hddl')
        parser.parse_problem(self.rover_path + 'p01.hddl')
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual(
            """==>
4 visit waypoint1
7 navigate rover0 waypoint1 waypoint0
8 unvisit waypoint1
11 nop
12 sample_soil rover0 rover0store waypoint0
15 communicate_soil_data2 rover0 general waypoint0 waypoint1
20 nop
23 drop rover0 rover0store
24 sample_rock rover0 rover0store waypoint0
27 communicate_rock_data2 rover0 general waypoint0 waypoint1
34 nop
35 calibrate rover0 camera0 objective0 waypoint0
38 nop
39 take_image rover0 waypoint0 objective1 camera0 low_res
44 nop
45 communicate_image_data rover0 general objective1 low_res waypoint0 waypoint1
root 0 16 28
0 get_soil_data waypoint0 -> m7_get_soil_data 2 3 4 5
5 do_navigate2 rover0 waypoint1 waypoint0 -> m3_do_navigate2 7
9 empty_store rover0store rover0 -> m5_empty_store 11
13 send_soil_data rover0 waypoint0 -> m9_send_soil_data 15
16 get_rock_data waypoint0 -> m10_get_rock_data 18 19 20 21
21 empty_store rover0store rover0 -> m6_empty_store 23
25 send_rock_data rover0 waypoint0 -> m12_send_rock_data 27
28 get_image_data objective1 low_res -> m13_get_image_data 30 31 32 33
36 do_navigate1 rover0 waypoint0 -> m0_do_navigate1 38
40 send_image_data rover0 objective1 low_res -> m14_send_image_data 42 43
<==""",
            str(res.progress_tracker))
