import subprocess
import unittest
import unittest.mock
from unittest.mock import patch, mock_open
import os
import sys
import io

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

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
from Solver.Models.model import Model
from Tools.output_plan_reader import read_plan, display_plan
from Tests.TestTools.env_setup import env_setup


class RunnerTests(unittest.TestCase):
    original_dir = os.getcwd()
    maxDiff = None

    def setUp(self) -> None:
        self.basic_domain_path = "Examples/Basic/basic.hddl"
        self.basic_pb1_path = "Examples/Basic/pb1.hddl"
        self.basic_domain_path_JSHOP = "Examples/JShop/basic/basic.jshop"
        self.basic_pb1_path_JSHOP = "Examples/JShop/basic/problem.jshop"
        self.test_tools_path = "TestTools/"
        self.blocksworld_path = "Examples/Blocksworld/"
        self.rover_path = "Examples/IPC_Tests/Rover/"
        self.rover_col_path = "Examples/Rover/"
        self.IPC_Tests_path = "Examples/IPC_Tests/"
        os.chdir(self.original_dir)
        self.expected_error_message = """usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]
                 [-paramSelectPath PARAMSELECTPATH]
                 [-searchQueueName SEARCHQUEUENAME]
                 [-searchQueuePath SEARCHQUEUEPATH]
                 [-progressTrackerName PROGRESSTRACKERNAME]
                 [-progressTrackerPath PROGRESSTRACKERPATH]
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH] [-O]
                 [D] [P]
runner.py: error: Incorrect Usage."""

        if sys.platform == "win32":
            self.python_command = "python"
        else:
            self.python_command = "python3"
        Model.model_counter = 0

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
                        "Runner.__init__() missing 1 required positional argument: 'problem_path'" == str(
            error.exception))

    def test_load_incompatible_files(self):
        # Test loading incompatible files
        with self.assertRaises(TypeError) as error:
            controller = Runner(self.basic_domain_path, self.basic_pb1_path_JSHOP)
            controller.parse_domain()
            controller.parse_problem()
        self.assertEqual("Problem file type (jshop) does not match domain file type (hddl)", str(error.exception))

    def test_load_unknown_file_type(self):
        # Test loading a txt file
        with self.assertRaises(TypeError) as error:
            cont = Runner("Tests/TestTools/fakeDomain.txt", self.basic_pb1_path)
            cont.parse_domain()
        self.assertEqual("Unknown descriptor type (txt)", str(error.exception))

    def test_load_no_file_type(self):
        # Load file with no suffix
        with self.assertRaises(TypeError) as error:
            controller = Runner("Tests/TestTools/fakeDomain2", self.basic_pb1_path)
            controller.parse_domain()
        self.assertEqual("Unknown descriptor type (None)", str(error.exception))

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

    def test_load_module_not_in_file(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        with self.assertRaises(ModuleNotFoundError) as error:
            controller.set_heuristic_from_file('FakeDistance',
                                           'Solver/Heuristics/hamming_distance.py')
        self.assertEqual("Module with the name 'FakeDistance' was not found in the file "
                         "'Solver/Heuristics/hamming_distance.py'", str(error.exception))

    def test_runner_setting_heuristic_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_heuristic_from_file('HammingDistance',
                                           'Solver/Heuristics/hamming_distance.py')
        self.assertEqual(HammingDistance.__name__, type(controller.solver.search_models.heuristic).__name__)

        controller.set_heuristic_from_file('TreeDistance',
                                           'Solver/Heuristics/tree_distance.py')
        self.assertEqual(TreeDistance.__name__, type(controller.solver.search_models.heuristic).__name__)

    def test_runner_setting_solver_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_solver_from_file('TotalOrderSolver', 'Solver/Solving_Algorithms/total_order.py')
        self.assertEqual(TotalOrderSolver.__name__, type(controller.solver).__name__)

    def test_runner_set_solver(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.set_solver(TotalOrderSolver(controller.domain, controller.problem))
        self.assertEqual(TotalOrderSolver.__name__, type(controller.solver).__name__)

    def test_runner_setting_SearchQueue_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_search_queue_from_file('GBFSSearchQueue',
                                              'Solver/Search_Queues/Greedy_Best_First_Search_Queue.py')
        self.assertEqual(GBFSSearchQueue.__name__, type(controller.solver.search_models).__name__)

    def test_runner_setting_SearchQueue_from_command_line(self):
        error_raised = False
        msg = None
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-searchQueueName", "GBFSSearchQueue", "-searchQueuePath",
                                  "Solver/Search_Queues/Greedy_Best_First_Search_Queue.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            error_raised = True
        self.assertFalse(error_raised, msg)

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
        controller.set_progress_tracker_from_file('PandaVerifyFormatTracker',
                                                  'Solver/Progress_Tracking/panda_verify_format.py')
        self.assertEqual(PandaVerifyFormatTracker.__name__, controller.solver.progress_tracker.__name__)

    def test_runner_setting_model_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_model_from_file('PandaVerifyModel', 'Solver/Models/PandaVerifyModel.py')
        self.assertEqual(PandaVerifyModel.__name__, controller.solver.ModelClass.__name__)

    def test_runner_parse_jshop(self):
        controller = Runner(self.basic_domain_path_JSHOP, self.basic_pb1_path_JSHOP)
        controller.parse_domain()
        controller.parse_problem()
        self.assertEqual(2, len(controller.domain.actions))
        self.assertEqual(2, len(controller.domain.methods))
        self.assertEqual(1, len(controller.domain.tasks))

    def test_set_early_precon_checker(self):
        controller = Runner(self.basic_domain_path_JSHOP, self.basic_pb1_path_JSHOP)
        controller.set_early_task_precon_checker(False)
        self.assertEqual(False, controller.solver.task_expansion_given_param_check)

    def test_runner_solving_basic(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        res = controller.solve()
        self.assertIsNotNone(res, 'Plan not found')

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_output_basic(self, mock_stdout):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        res = controller.solve()

        controller.output_result(res)

        # self.assertEqual("Test", captured_output.getvalue())
        self.assertEqual(mock_stdout.getvalue(), """
Actions Taken:
drop - kiwi
pickup - banjo

Operations Taken:
swap - banjo kiwi
have_second - banjo kiwi
drop - kiwi
pickup - banjo

Search Models Created During Search: 3
""")

    @patch('runner.open', new_callable=mock_open)
    @patch('runner.os')
    def test_output_result_file_no_output_dir(self, mock_os, mock_open_method):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)
        res = solver.solve()

        mock_os.path.isdir.return_value = False

        Runner.output_result_file(res, 'testing_output.txt')
        mock_os.path.isdir.assert_called_once_with('output')
        mock_os.mkdir.assert_called_once_with('output')

        mock_open_method.assert_called_once_with('output/testing_output.txt', 'w')
        handle = mock_open_method()
        handle.write.assert_called_once_with(str(res.progress_tracker))
        handle.close.assert_called_once()

    @patch('runner.open', new_callable=mock_open)
    def test_output_result_file_unknown_suffix(self, mock_open_method):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)
        res = solver.solve()

        with self.assertRaises(ValueError) as error:
            Runner.output_result_file(res, 'testing_output.unknownSuffix')
        self.assertEqual("Output Suffix unknownSuffix not recognised", str(error.exception))

    @patch('runner.os')
    def test_check_file_exists(self, mock_os):
        mock_os.path.exists.return_value = False
        with self.assertRaises(FileNotFoundError) as error:
            Runner._Runner__check_file_exists('fakePath.txt', None)
        self.assertEqual("File fakePath.txt could not be found", str(error.exception))


class RunnerCommandLineTests(unittest.TestCase):
    original_dir = os.getcwd()
    maxDiff = None

    def setUp(self) -> None:
        self.basic_domain_path = "Examples/Basic/basic.hddl"
        self.basic_pb1_path = "Examples/Basic/pb1.hddl"
        self.basic_pb1_path_SHOP = "Examples/Basic/pb1.shop"
        self.test_tools_path = "TestTools/"
        self.blocksworld_path = "Examples/Blocksworld/"
        self.rover_path = "Examples/IPC_Tests/Rover/"
        self.rover_col_path = "Examples/Rover/"
        self.IPC_Tests_path = "Examples/IPC_Tests/"
        os.chdir(self.original_dir)
        self.expected_error_message = """usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]
                 [-paramSelectPath PARAMSELECTPATH]
                 [-searchQueueName SEARCHQUEUENAME]
                 [-searchQueuePath SEARCHQUEUEPATH]
                 [-progressTrackerName PROGRESSTRACKERNAME]
                 [-progressTrackerPath PROGRESSTRACKERPATH]
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH] [-O]
                 [D] [P]
runner.py: error: Incorrect Usage."""

        self.expected_help_menu_1 = """usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]
                 [-paramSelectPath PARAMSELECTPATH]
                 [-searchQueueName SEARCHQUEUENAME]
                 [-searchQueuePath SEARCHQUEUEPATH]
                 [-progressTrackerName PROGRESSTRACKERNAME]
                 [-progressTrackerPath PROGRESSTRACKERPATH]
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH] [-O]
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
  -O                    Flag to disable printing resulting plan
"""
        self.expected_help_menu_2 = """usage: runner.py [-h] [-w W] [-solverModName SOLVERMODNAME]
                 [-solverPath SOLVERPATH] [-heuModName HEUMODNAME]
                 [-heuPath HEUPATH] [-paramSelectName PARAMSELECTNAME]
                 [-paramSelectPath PARAMSELECTPATH]
                 [-searchQueueName SEARCHQUEUENAME]
                 [-searchQueuePath SEARCHQUEUEPATH]
                 [-progressTrackerName PROGRESSTRACKERNAME]
                 [-progressTrackerPath PROGRESSTRACKERPATH]
                 [-modelModName MODELMODNAME] [-modelPath MODELPATH] [-O]
                 [D] [P]

positional arguments:
  D                     File path to Domain File
  P                     File path to Problem File

options:
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
  -O                    Flag to disable printing resulting plan
"""

        if sys.platform == "win32":
            self.python_command = "python"
        else:
            self.python_command = "python3"

    def test_file_writing_command_line_args(self):
        try:
            res = subprocess.run(
                [self.python_command, "./runner.py", "Examples/Basic/basic.hddl", "Examples/Basic/pb1.hddl",
                 "-w", "runner_test_basic_p1"],
                check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            print(msg)
            res = None

        self.assertIn("""Actions Taken:
drop - kiwi
pickup - banjo

Operations Taken:
swap - banjo kiwi
have_second - banjo kiwi
drop - kiwi
pickup - banjo

Search Models Created During Search: 3
""", res)
        self.assertTrue(os.path.exists("output/runner_test_basic_p1"))

    def test_runner_command_line_incorrect_args(self):
        error_raised = False
        try:
            res = subprocess.run(
                [self.python_command, "./runner.py", "Examples/Basic/basic.hddl", "-w", "runner_test_basic_p1"],
                check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            # msg = msg[434:]   # This is for debugger inspection only
            self.assertEqual(
                self.expected_error_message + " Correct usage 'python runner.py <domain.suffix> <problem.suffix>'\n",
                msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_help(self):
        try:
            res = subprocess.run([self.python_command, "./runner.py", "-h"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            raise RuntimeError(msg)

        self.assertTrue(res == self.expected_help_menu_1 or res == self.expected_help_menu_2)

    def test_runner_command_line_heuname_only(self):
        error_raised = False
        try:
            res = subprocess.run(
                [self.python_command, "./runner.py", "../Examples/Basic/basic.hddl", "../Examples/Basic/pb1.hddl",
                 "-heuModName", "PredicateDistanceToGoal"],
                check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            self.assertEqual(
                self.expected_error_message + " Either both '-heuModName' and '-heuPath' need to be set or both need "
                                              "to be empty\n",
                msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_heupath_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-heuPath", "Solver/Heuristics/hamming_distance.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            self.assertEqual(
                self.expected_error_message + " Either both '-heuModName' and '-heuPath' need to be set or both need "
                                              "to be empty\n",
                msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_setting_heuristic_from_command_line(self):
        error_raised = False
        msg = None
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-heuModName", "HammingDistance", "-heuPath",
                                  "Solver/Heuristics/hamming_distance.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            error_raised = True
        self.assertFalse(error_raised, msg)

    def test_runner_setting_parameter_selector_from_path(self):
        controller = Runner(self.basic_domain_path, self.basic_pb1_path)
        controller.parse_domain()
        controller.parse_problem()
        controller.set_parameter_selector_from_file('AllParameters',
                                                    'Solver/Parameter_Selection/All_Parameters.py')
        self.assertEqual(AllParameters.__name__, type(controller.solver.parameter_selector).__name__)

        controller.set_parameter_selector_from_file('RequirementSelection',
                                                    'Solver/Parameter_Selection/Requirement_Selection.py')
        self.assertEqual(RequirementSelection.__name__, type(controller.solver.parameter_selector).__name__)

    def test_runner_setting_parameter_selector_from_command_line(self):
        error_raised = False
        msg = None
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "/Examples/Basic/pb1.hddl", "-paramSelectName", "RequirementSelection"
                                                                                  "-paramSelectPath",
                                  "Solver/Parameter_Selection/Requirement_Selection.py"],
                                 stderr=subprocess.PIPE)
        except Exception as e:
            msg = e.stderr
            error_raised = True
        self.assertFalse(error_raised, msg)

    def test_runner_command_line_paramname_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-paramSelectName", "PredicateDistanceToGoal"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            self.assertEqual(
                self.expected_error_message + " Either both '-paramSelectName' and '-paramSelectPath' need to be set "
                                              "or both need to be empty\n",
                msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_parampath_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Tests/Examples/Basic/pb1.hddl", "-paramSelectPath",
                                  "Solver/Heuristics/hamming_distance.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            self.assertEqual(
                self.expected_error_message + " Either both '-paramSelectName' and '-paramSelectPath' need to be set "
                                              "or both need to be empty\n",
                msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_solvername_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-solverModName", "PredicateDistanceToGoal"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            expected_msg = self.expected_error_message + (" Either both '-solverModName' and '-solverPath' need to be "
                                                          "set or both need to be empty\n")
            self.assertEqual(expected_msg, msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_solverpath_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-solverPath", "Solver/Heuristics/hamming_distance.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            expected_msg = self.expected_error_message + (" Either both '-solverModName' and '-solverPath' need to be "
                                                          "set or both need to be empty\n")
            self.assertEqual(expected_msg, msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_searchQueueName_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-searchQueueName", "GBFSSearchQueue"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            expected_msg = self.expected_error_message + (" Either both '-searchQueueName' and '-searchQueuePath' need "
                                                          "to be set or both need to be empty\n")
            self.assertEqual(expected_msg, msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_command_line_searchQueuePath_only(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-searchQueuePath",
                                  "Solver/Search_Queues/Greedy_Best_First_Search_Queue.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            expected_msg = self.expected_error_message + (" Either both '-searchQueueName' and '-searchQueuePath' need "
                                                          "to be set or both need to be empty\n")
            self.assertEqual(expected_msg, msg)
            error_raised = True
        self.assertTrue(error_raised, "An Error Was not Raised When Running the Command")

    def test_runner_setting_solver_from_command_line(self):
        error_raised = False
        msg = None
        try:
            res = subprocess.run(
                [self.python_command, "./runner.py", "Examples/Basic/basic.hddl", "Examples/Basic/pb1.hddl",
                 "-solverModName", "TotalOrderSolver", "-solverPath", "Solver/Solving_Algorithms/total_order.py"],
                check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr  # This is for debugger inspection only
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, msg)

    def test_runner_setting_progressTracker_from_command_line(self):
        error_raised = False
        msg = None
        try:
            res = subprocess.run([
                self.python_command, "./runner.py", "Examples/Basic/basic.hddl", "Examples/Basic/pb1.hddl",
                "-progressTrackerName", "SequentialTracker", "-progressTrackerPath",
                "Solver/Progress_Tracking/sequential_progress_tracker.py"],
                check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            error_raised = True
        self.assertFalse(error_raised, msg)

    def test_runner_setting_model_from_command_line(self):
        error_raised = False
        try:
            res = subprocess.run([self.python_command, "./runner.py", "Examples/Basic/basic.hddl",
                                  "Examples/Basic/pb1.hddl", "-modelModName", "PandaVerifyModel", "-modelPath",
                                  "Solver/Models/PandaVerifyModel.py"],
                                 check=True, capture_output=True, text=True).stdout
        except Exception as e:
            msg = e.stderr
            print(msg)
            error_raised = True
        self.assertFalse(error_raised, "An Error Was Raised When Running the Command")
