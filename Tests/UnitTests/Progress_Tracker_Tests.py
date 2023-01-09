import os.path
import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from Solver.Models.PandaVerifyModel import PandaVerifyDefaultModel
from runner import Runner


class ProgressTrackerTests(unittest.TestCase):

    def setUp(self):
        self.basic_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"
        self.rover_path = "../Examples/Rover/"
        self.IPC_test_path = "../Examples/IPC_Tests/"

    def test_basic_pandaverify_output(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.basic_path)
        parser.parse_problem(self.basic_pb1_path)
        solver.set_model_class(PandaVerifyDefaultModel)
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 drop kiwi
2 pickup banjo
root 0
0 swap banjo kiwi -> have_second 1 2
<==""", str(res.progress_tracker))

    def test_basic_pandaverify_output_file(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.basic_path)
        parser.parse_problem(self.basic_pb1_path)
        solver.set_model_class(PandaVerifyDefaultModel)
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        Runner.output_result_file(res, "basic_test_panda.txt")

        # Check output file exists
        self.assertEqual(True, os.path.isfile('output/basic_test_panda.txt'))

        # Check contents of output file
        with open('output/basic_test_panda.txt') as f:
            file_contents = f.read()

        self.assertEqual("""==>
1 drop kiwi
2 pickup banjo
root 0
0 swap banjo kiwi -> have_second 1 2
<==""", file_contents)

    def test_ipc_test_1(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test01_empty_method/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test01_empty_method/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
root 0
0 task1 -> donothing
<==""", str(res.progress_tracker))

    def test_ipc_test_2(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test02_forall/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test02_forall/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 noop
root 0
0 task1 -> donothing 1
<==""", str(res.progress_tracker))

    def test_ipc_test_3(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test03_forall1/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test03_forall1/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 noop f
root 0
0 task1 -> donothing 1
<==""", str(res.progress_tracker))

    def test_ipc_test_4(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test04_no_abstracts/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test04_no_abstracts/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
0 noop
root 0
<==""", str(res.progress_tracker))

    def test_ipc_test_5(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test05_constants_in_domain/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test05_constants_in_domain/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 noop a
root 0
0 task1 -> donothing 1
<==""", str(res.progress_tracker))

    def test_ipc_test_6(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test06_synonymes/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test06_synonymes/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 noop1
2 noop2
4 noop1
5 noop2
7 noop1
8 noop2
10 noop1
11 noop2
root 0 3 6 9
0 task1 -> sequence1 1 2
3 task2 -> sequence2 4 5
6 task3 -> sequence3 7 8
9 task4 -> sequence4 10 11
<==""", str(res.progress_tracker))

    def test_ipc_test_7(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.IPC_test_path + "test07_arguments/domain.hddl")
        parser.parse_problem(self.IPC_test_path + "test07_arguments/problem.hddl")
        solver.set_model_class(PandaVerifyDefaultModel)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual("""==>
1 noop b b
root 0
0 task1 -> donothing 1
<==""", str(res.progress_tracker))

    def test_rover_1_pandaverify_output(self):
        domain, problem, parser, solver = env_setup(True, True)
        parser.parse_domain(self.rover_path + 'domain.hddl')
        parser.parse_problem(self.rover_path + 'p01.hddl')
        solver.set_model_class(PandaVerifyDefaultModel)
        solver.set_progress_tracker(PandaVerifyFormatTracker)

        res = solver.solve()

        print(res.progress_tracker)
        self.assertEqual(
            """==>
5 visit waypoint1
8 navigate rover0 waypoint1 waypoint0
7 unvisit waypoint1
9 nop
3 sample_soil rover0 rover0store waypoint0
10 communicate_soil_data2 rover0 general waypoint0 waypoint1
16 nop
17 drop rover0 rover0store
14 sample_rock rover0 rover0store waypoint0
18 communicate_rock_data2 rover0 general waypoint0 waypoint1
26 nop
25 calibrate rover0 camera0 objective0 waypoint0
27 nop
22 take_image rover0 waypoint0 objective1 camera0 low_res
30 nop
29 communicate_image_data rover0 general objective1 low_res waypoint0 waypoint1
root 0 11 19
0 get_soil_data waypoint0 -> m7_get_soil_data 1 2 3 4
1 do_navigate1 rover0 waypoint0 -> m1_do_navigate1 5 6 7
6 do_navigate2 rover0 waypoint1 waypoint0 -> m3_do_navigate2 8
2 empty_store rover0store rover0 -> m5_empty_store 9
4 send_soil_data rover0 waypoint0 -> m9_send_soil_data 10
11 get_rock_data waypoint0 -> m10_get_rock_data 12 13 14 15
12 do_navigate1 rover0 waypoint0 -> m0_do_navigate1 16
13 empty_store rover0store rover0 -> m6_empty_store 17
15 send_rock_data rover0 waypoint0 -> m12_send_rock_data 18
19 get_image_data objective1 low_res -> m13_get_image_data 20 21 22 23
20 do_calibrate rover0 camera0 -> m15_do_calibrate 24 25
24 do_navigate1 rover0 waypoint0 -> m0_do_navigate1 26
21 do_navigate1 rover0 waypoint0 -> m0_do_navigate1 27
23 send_image_data rover0 objective1 low_res -> m14_send_image_data 28 29
28 do_navigate1 rover0 waypoint0 -> m0_do_navigate1 30
<==""",
            str(res.progress_tracker))
