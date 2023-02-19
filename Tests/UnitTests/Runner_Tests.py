import subprocess
import unittest
import os
from Tests.UnitTests.TestTools.env_setup import env_setup
from Tests.Evaluation.output_plan_reader import read_plan, display_plan
from runner import Runner
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Parsers.HDDL_Parser import HDDLParser
from Solver.Heuristics.hamming_distance import HammingDistance
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Heuristics.delete_relaxed import DeleteRelaxed
from Solver.Parameter_Selection.All_Parameters import AllParameters
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection
from Solver.Solving_Algorithms.total_order import TotalOrderSolver
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from Solver.Models.PandaVerifyModel import PandaVerifyModel


class RunnerTests(unittest.TestCase):
    original_dir = os.getcwd()

    def setUp(self) -> None:
        self.basic_domain_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"
        self.basic_pb1_path_SHOP = "../Examples/Basic/pb1.shop"
        self.test_tools_path = "TestTools/"
        self.blocksworld_path = "../Examples/Blocksworld/"
        self.rover_path = "../Examples/IPC_Tests/Rover/"
        self.rover_col_path = "../Examples/Rover/"
        self.IPC_Tests_path = "../Examples/IPC_Tests/"
        os.chdir(self.original_dir)

        self.expected_error_message = """usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]\r
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]\r
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]\r
                 [-paramSelectPath PARAMSELECTPATH]\r
                 [-searchQueueName SEARCHQUEUENAME]\r
                 [-searchQueuePath SEARCHQUEUEPATH]\r
                 [-progressTrackerName PROGRESSTRACKERNAME]\r
                 [-progressTrackerPath PROGRESSTRACKERPATH]\r
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH]\r
                 [D] [P]\r
runner.py: error: Incorrect Usage."""

    def test_load_unknown_domain(self):
        # Test loading unknown domain file
        with self.assertRaises(FileNotFoundError) as error:
            cont = Runner("../Examples/WrongBasic/basic.hddl", self.basic_pb1_path)
            cont.parse_domain()
        self.assertEqual("Domain file entered could not be found. ({})".format("../Examples/WrongBasic/basic.hddl"),
                         str(error.exception))

    def test_load_unknown_problem(self):
        # Test loading unknown problem file
        with self.assertRaises(FileNotFoundError) as error:
            cont = Runner(self.basic_domain_path, "../Examples/WrongBasic/pb1.hddl")
            cont.parse_domain()
            cont.parse_problem()
        self.assertEqual("Problem file entered could not be found. ({})".format("../Examples/WrongBasic/pb1.hddl"),
                         str(error.exception))

    def test_load_known_file(self):
        # Test loading basic domain and basic pb1
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)

    def test_load_one_file(self):
        # Test only passing in one file path
        with self.assertRaises(Exception) as error:
            Runner(self.basic_domain_path)
        self.assertTrue("__init__() missing 1 required positional argument: 'problem_path'" == str(error.exception) or
                        "Runner.__init__() missing 1 required positional argument: 'problem_path'" == str(error.exception))

    @unittest.skip
    def test_load_incompatible_files(self):
        # Test loading incompatible files
        with self.assertRaises(TypeError) as error:
            Runner(self.basic_domain_path, self.basic_pb1_path_SHOP)
        self.assertEqual("Problem file type (shop) does not match domain file type (hddl)", str(error.exception))

    def test_load_unknown_file_type(self):
        # Test loading a txt file
        with self.assertRaises(TypeError) as error:
            cont = Runner("TestTools/fakeDomain.txt", self.basic_pb1_path)
            cont.parse_domain()
        self.assertEqual("Unknown descriptor type (txt)", str(error.exception))

        # # Load file with no suffix
        # with self.assertRaises(IOError) as error:
        #     Runner("TestTools/fakeDomain2", self.basic_pb1_path)
        # self.assertEqual("File type not identified. (TestTools/fakeDomain2)", str(error.exception))

    def test_file_writing_command_line_args(self):
        os.chdir("../..")
        res = os.popen("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -w runner_test_basic_p1")
        output = res.read()
        self.assertIn("""Actions Taken:
drop - kiwi
pickup - banjo

Operations Taken:
swap - banjo kiwi
have_second - banjo kiwi
drop - kiwi
pickup - banjo

Search Models Created During Search: 3
""", output)
        self.assertTrue(os.path.exists("output/runner_test_basic_p1"))

    def test_file_writing_and_reading(self):
        if os.path.isfile("output/runner_test_basic_p1"):
            os.remove("output/runner_test_basic_p1")

        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)
        res = solver.solve()
        Runner.output_result_file(res, "runner_test_basic_p1")
        plan = read_plan("output/runner_test_basic_p1")

        self.assertEqual(res.model_number, plan.model_number)
        self.assertEqual(res.current_state, plan.current_state)

    def test_runner_command_line_incorrect_args(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl -w runner_test_basic_p1",
                                          stderr=subprocess.PIPE)
            output, error = res.communicate()
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            # msg = msg[434:]   # This is for debugger inspection only
            self.assertEqual(self.expected_error_message + " Correct usage 'python runner.py <domain.suffix> <problem.suffix>'\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")
        os.chdir(original_dir)

    def test_runner_command_line_help(self):
        os.chdir("../..")
        res = os.popen("python ./runner.py -h")
        output = res.read()
        self.assertEqual("""usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]
                 [-paramSelectPath PARAMSELECTPATH]
                 [-searchQueueName SEARCHQUEUENAME]
                 [-searchQueuePath SEARCHQUEUEPATH]
                 [-progressTrackerName PROGRESSTRACKERNAME]
                 [-progressTrackerPath PROGRESSTRACKERPATH]
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH]
                 [D] [P]

positional arguments:
  D                     File path to Domain File
  P                     File path to Problem File

optional arguments:
  -h, --help            show this help message and exit
  -w W                  File path to Write Resulting Plan File
  -solverModName SOLVERMODNAME
                        Name of Solver Class
  -solverPath SOLVERPATH
                        File path to Solver File
  -heuModName HEUMODNAME
                        Name of Heuristic Class
  -heuPath HEUPATH      File path to Heuristic File
  -paramSelectName PARAMSELECTNAME
                        Name of Parameter Selector Class
  -paramSelectPath PARAMSELECTPATH
                        File path to Parameter Selector File
  -searchQueueName SEARCHQUEUENAME
                        Name of SearchQueue Class
  -searchQueuePath SEARCHQUEUEPATH
                        File path to SearchQueue File
  -progressTrackerName PROGRESSTRACKERNAME
                        Name of Progress Tracker Class
  -progressTrackerPath PROGRESSTRACKERPATH
                        File path to Progress Tracker File
  -modelModName MODELMODNAME
                        Name of Model Class
  -modelPath MODELPATH  File path to Model File
""", output)

    def test_runner_command_line_heupath_or_heuname_only(self):
        # Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuModName PredicateDistanceToGoal -heuPath Solver/Heuristics/hamming_distance.py
        os.chdir("../..")

        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuModName PredicateDistanceToGoal",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-heuModName' and '-heuPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuPath Solver/Heuristics/hamming_distance.py",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-heuModName' and '-heuPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_setting_heuristic_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_heuristic_from_file('HammingDistance', '../../Solver/Heuristics/hamming_distance.py')
        self.assertEqual(HammingDistance.__name__, type(controller.solver.search_models.heuristic).__name__)

        controller.set_heuristic_from_file('TreeDistance', '../../Solver/Heuristics/tree_distance.py')
        self.assertEqual(TreeDistance.__name__, type(controller.solver.search_models.heuristic).__name__)

    def test_runner_setting_heuristic_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuModName HammingDistance"
                                          "  -heuPath Solver/Heuristics/hamming_distance.py",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)

    def test_runner_setting_parameter_selector_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_parameter_selector_from_file('AllParameters', '../../Solver/Parameter_Selection/All_Parameters.py')
        self.assertEqual(AllParameters.__name__, type(controller.solver.parameter_selector).__name__)

        controller.set_parameter_selector_from_file('RequirementSelection', '../../Solver/Parameter_Selection/Requirement_Selection.py')
        self.assertEqual(RequirementSelection.__name__, type(controller.solver.parameter_selector).__name__)

    def test_runner_setting_parameter_selector_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -paramSelectName RequirementSelection"
                                          " -paramSelectPath Solver/Parameter_Selection/Requirement_Selection.py",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)

    def test_runner_command_line_parampath_or_paramname_only(self):
        # Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuModName PredicateDistanceToGoal -heuPath Solver/Heuristics/hamming_distance.py
        os.chdir("../..")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -paramSelectName PredicateDistanceToGoal",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-paramSelectName' and '-paramSelectPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -paramSelectPath Solver/Heuristics/hamming_distance.py",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-paramSelectName' and '-paramSelectPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_solverpath_or_solvername_only(self):
        # Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -heuModName PredicateDistanceToGoal -heuPath Solver/Heuristics/hamming_distance.py
        os.chdir("../..")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -solverModName PredicateDistanceToGoal",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-solverModName' and '-solverPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -solverPath Solver/Heuristics/hamming_distance.py",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-solverModName' and '-solverPath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_searchQueueName_or_searchQueuePath_only(self):
        # Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -searchQueueName GBFSSearchQueue -searchQueuePath Solver/Search_Queues/Greedy_Best_First_Search_Queue.py
        os.chdir("../..")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -searchQueueName GBFSSearchQueue",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-searchQueueName' and '-searchQueuePath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -searchQueuePath Solver/Search_Queues/Greedy_Best_First_Search_Queue.py",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")
            self.assertEqual(self.expected_error_message + " Either both '-searchQueueName' and '-searchQueuePath' need to be set or both need to be empty\r\n", msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_setting_solver_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_solver_from_file('TotalOrderSolver', '../../Solver/Solving_Algorithms/total_order.py')
        self.assertEqual(TotalOrderSolver.__name__, type(controller.solver).__name__)

    def test_runner_setting_solver_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl -solverModName TotalOrderSolver"
                                          " -solverPath Solver/Solving_Algorithms/total_order.py",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)

    def test_runner_setting_SearchQueue_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_search_queue_from_file('GBFSSearchQueue', '../../Solver/Search_Queues/Greedy_Best_First_Search_Queue.py')
        self.assertEqual(GBFSSearchQueue.__name__, type(controller.solver.search_models).__name__)

    def test_runner_setting_SearchQueue_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output("python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl "
                                          "-searchQueueName GBFSSearchQueue -searchQueuePath Solver/Search_Queues/Greedy_Best_First_Search_Queue.py",
                                          stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)

    def test_runner_setting_heu_paramselec_solver_searchQueue(self):
        controller = Runner(self.rover_col_path + "domain.hddl", self.rover_col_path + "p02.hddl")
        controller.parse_domain()
        controller.parse_problem()
        controller.set_solver(TotalOrderSolver)
        controller.set_heuristic(DeleteRelaxed)
        controller.set_parameter_selector(AllParameters)
        controller.set_search_queue(GBFSSearchQueue)

        self.assertEqual(TotalOrderSolver.__name__, type(controller.solver).__name__)
        self.assertEqual(DeleteRelaxed.__name__, type(controller.solver.search_models.heuristic).__name__)
        self.assertEqual(AllParameters.__name__, type(controller.solver.parameter_selector).__name__)
        self.assertEqual(GBFSSearchQueue.__name__, type(controller.solver.search_models).__name__)

    def test_runner_setting_progressTracker_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_progress_tracker_from_file('PandaVerifyFormatTracker', '../../Solver/Progress_Tracking/panda_verify_format.py')
        self.assertEqual(PandaVerifyFormatTracker.__name__, controller.solver.progress_tracker.__name__)

    def test_runner_setting_progressTracker_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl "
                "-progressTrackerName SequentialTracker -progressTrackerPath Solver/Progress_Tracking/sequential_progress_tracker.py",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)

    @unittest.skip
    def test_runner_setting_model_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_model_from_file('PandaVerifyModel',
                                       '../../Solver/Models/PandaVerifyModel.py')
        self.assertEqual(PandaVerifyModel.__name__, controller.solver.ModelClass.__name__)


    @unittest.skip
    def test_runner_setting_model_from_command_line(self):
        original_dir = os.getcwd()
        os.chdir("../..")
        error_raised = False
        try:
            res = subprocess.check_output(
                "python ./runner.py Tests/Examples/Basic/basic.hddl Tests/Examples/Basic/pb1.hddl "
                "-modelModName PandaVerifyModel -modelPath Solver/Models/PandaVerifyModel.py",
                stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr.decode("utf-8")  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
        os.chdir(original_dir)
