import argparse
import os
import pickle
import sys
import importlib.util
import inspect
from abc import ABCMeta
from Parsers.HDDL_Parser import HDDLParser
from Parsers.JSHOP_Parser import JSHOPParser
from Solver.Solving_Algorithms.solver import Solver
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Solver.Heuristics.Heuristic import Heuristic
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Solver.Models.default_model import DefaultModel
from Solver.Search_Queues.search_queue import SearchQueue
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker


class Runner:
    def __init__(self, domain_path, problem_path):
        # Necessary variables
        self.parser = None
        self.suffix = None
        self.domain = Domain(None)
        self.problem = Problem(self.domain)
        self.domain.add_problem(self.problem)
        self.solver = PartialOrderSolver(self.domain, self.problem)
        self.domain_path = domain_path
        self.problem_path = problem_path

    def parse_domain(self) -> None:
        self.__check_file_exists(self.domain_path, "Domain")
        # Check for valid suffix
        self.suffix = self.__get_suffix(self.domain_path)
        if self.suffix == "hddl":
            self.parser = HDDLParser(self.domain, self.problem)
        elif self.suffix == "jshop":
            self.parser = JSHOPParser(self.domain, self.problem)
        else:
            raise TypeError("Unknown descriptor type ({})".format(self.suffix))
        self.parser.parse_domain(self.domain_path)

    def parse_problem(self) -> None:
        self.__check_file_exists(self.problem_path, "Problem")
        suffix = self.__get_suffix(self.problem_path)
        if suffix == self.suffix:
            self.parser.parse_problem(self.problem_path)
        else:
            raise TypeError("Problem file type ({}) does not match domain file type ({})".format(suffix, self.suffix))

    def _get_module_from_file(self, module_name: str, file_path: str):
        # Load Class
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name == module_name:
                return obj

    def set_solver(self, solver: type(Solver)) -> None:
        if type(solver) == type or type(solver) == ABCMeta:
            solver = solver(self.domain, self.problem)
        assert isinstance(solver, Solver)
        self.solver = solver

    def set_solver_from_file(self, module_name: str, file_path: str) -> None:
        self.set_solver(self._get_module_from_file(module_name, file_path))

    def set_heuristic(self, heuristic: type(Heuristic)) -> None:
        self.solver.set_heuristic(heuristic)

    def set_heuristic_from_file(self, module_name: str, file_path: str) -> None:
        self.set_heuristic(self._get_module_from_file(module_name, file_path))

    def set_parameter_selector(self, param_selector: type(ParameterSelector)) -> None:
        self.solver.set_parameter_selector(param_selector)

    def set_parameter_selector_from_file(self, module_name: str, file_path: str) -> None:
        self.set_parameter_selector(self._get_module_from_file(module_name, file_path))

    def set_search_queue(self, search_queue: type(SearchQueue)) -> None:
        self.solver.set_search_queue(search_queue)

    def set_search_queue_from_file(self, module_name: str, file_path: str) -> None:
        self.set_search_queue(self._get_module_from_file(module_name, file_path))

    def set_progress_tracker(self, progress_tracker: type(SequentialTracker)):
        self.solver.set_progress_tracker(progress_tracker)

    def set_progress_tracker_from_file(self, module_name: str, file_path: str):
        self.set_progress_tracker(self._get_module_from_file(module_name, file_path))

    def set_model_from_file(self, model_mod_name: str, model_file: str):
        self.set_model(self._get_module_from_file(model_mod_name, model_file))

    def set_model(self, model_class: type(DefaultModel)):
        self.solver.set_model_class(model_class)

    def set_early_task_precon_checker(self, v: bool) -> None:
        self.solver.task_expansion_given_param_check = v

    def solve(self) -> DefaultModel:
        return self.solver.solve()

    def output_result(self, search_result: DefaultModel) -> None:
        self.solver.output(search_result)

    @staticmethod
    def output_result_file(result: DefaultModel, write_file: str) -> None:
        # Check output folder exists
        if not os.path.isdir("output"):
            os.mkdir("output")

        file_suffix = Runner.__get_suffix(write_file)
        if file_suffix == 'txt':
            file = open("output/" + write_file, "w")
            file.write(str(result.progress_tracker))
            file.close()
        elif file_suffix is None or file_suffix.lower() == 'pickle':
            # Pickle output and write to file
            file = open("output/" + write_file, "wb")
            file.write(pickle.dumps(result))
            file.close()
        else:
            raise ValueError('Output Suffix {} not recognised'.format(file_suffix))

    @staticmethod
    def __check_file_exists(file_path: str, file_purpose: str = None) -> None:
        if not os.path.exists(file_path):
            if file_purpose is None:
                raise FileNotFoundError("File {} could not be found".format(file_path))
            else:
                raise FileNotFoundError("{} file entered could not be found. ({})".format(file_purpose, file_path))

    @staticmethod
    def __get_suffix(path: str) -> str:
        try:
            return path[path.rindex(".") + 1:]
        except ValueError:
            return None


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("Domain_File", metavar='D', type=str, nargs="?", help='File path to Domain File', default=None)
    argparser.add_argument("Problem_File", metavar='P', type=str, nargs="?", help='File path to Problem File', default=None)
    argparser.add_argument("-w", type=str, help='File path to Write Resulting Plan File', default=None)
    argparser.add_argument("-solverModName", type=str, help='Name of Solver Class', default=None)
    argparser.add_argument("-solverPath", type=str, help='File path to Solver File', default=None)
    argparser.add_argument("-heuModName", type=str, help='Name of Heuristic Class', default=None)
    argparser.add_argument("-heuPath", type=str, help='File path to Heuristic File', default=None)
    argparser.add_argument("-paramSelectName", type=str, help='Name of Parameter Selector Class', default=None)
    argparser.add_argument("-paramSelectPath", type=str, help='File path to Parameter Selector File', default=None)
    argparser.add_argument("-searchQueueName", type=str, help='Name of SearchQueue Class', default=None)
    argparser.add_argument("-searchQueuePath", type=str, help='File path to SearchQueue File', default=None)
    argparser.add_argument("-progressTrackerName", type=str, help='Name of Progress Tracker Class', default=None)
    argparser.add_argument("-progressTrackerPath", type=str, help='File path to Progress Tracker File', default=None)
    argparser.add_argument("-modelModName", type=str, help='Name of Model Class', default=None)
    argparser.add_argument("-modelPath", type=str, help='File path to Model File', default=None)
    argparser.add_argument('-O', action='store_false', help='Flag to disable printing resulting plan')
    argparser.format_help()
    args = argparser.parse_args()

    domain_file = args.Domain_File
    problem_file = args.Problem_File
    write_file = args.w
    solver_mod_name = args.solverModName
    solver_file = args.solverPath
    heuristic_mod_name = args.heuModName
    heuristic_file = args.heuPath
    param_mod_name = args.paramSelectName
    param_file = args.paramSelectPath
    searchQueue_mod_name = args.searchQueueName
    searchQueue_file = args.searchQueuePath
    progressTracker_mod_name = args.progressTrackerName
    progressTracker_file = args.progressTrackerPath
    model_mod_name = args.modelModName
    model_file = args.modelPath

    if solver_mod_name is not None and solver_file is None or \
            solver_mod_name is None and solver_file is not None:
        argparser.error(
            "Incorrect Usage. Either both '-solverModName' and '-solverPath' need to be set or both need to be empty")
    elif heuristic_mod_name is not None and heuristic_file is None or \
            heuristic_mod_name is None and heuristic_file is not None:
        argparser.error("Incorrect Usage. Either both '-heuModName' and '-heuPath' need to be set or both need to be empty")
    elif param_mod_name is not None and param_file is None or \
            param_mod_name is None and param_file is not None:
        argparser.error(
            "Incorrect Usage. Either both '-paramSelectName' and '-paramSelectPath' need to be set or both need to be empty")
    elif searchQueue_mod_name is not None and searchQueue_file is None or \
            searchQueue_mod_name is None and searchQueue_file is not None:
        argparser.error(
            "Incorrect Usage. Either both '-searchQueueName' and '-searchQueuePath' need to be set or both need to be empty")
    elif progressTracker_mod_name is not None and progressTracker_file is None or \
            progressTracker_mod_name is None and progressTracker_file is not None:
        argparser.error(
            "Incorrect Usage. Either both '-progressTrackerName' and '-progressTrackerPath' need to be set or both need to be empty")
    elif model_mod_name is not None and model_file is None or model_mod_name is None and model_file is not None:
        argparser.error(
            "Incorrect Usage. Either both '-modelModName' and '-modelPath' need to be set or both need to be empty")

    if domain_file is not None and problem_file is not None:
        # Setup runner object
        controller = Runner(domain_file, problem_file)

        # Parse domain and problem
        controller.parse_domain()
        controller.parse_problem()

        # Solver Selection
        if solver_mod_name is not None and solver_file is not None:
            controller.set_solver_from_file(solver_mod_name, solver_file)

        # Heuristic selection
        if heuristic_mod_name is not None and heuristic_file is not None:
            controller.set_heuristic_from_file(heuristic_mod_name, heuristic_file)

        # Parameter Selector Selection
        if param_mod_name is not None and param_file is not None:
            controller.set_parameter_selector_from_file(param_mod_name, param_file)

        # SearchQueue Selection
        if searchQueue_mod_name is not None and searchQueue_file is not None:
            controller.set_search_queue_from_file(searchQueue_mod_name, searchQueue_file)

        # Model Selection
        if model_mod_name is not None and model_file is not None:
            controller.set_model_from_file(model_mod_name, model_file)

        # Progress Tracker Selection
        if progressTracker_mod_name is not None and progressTracker_file is not None:
            controller.set_progress_tracker_from_file(progressTracker_mod_name, progressTracker_file)

        # Initiate solving
        result = controller.solve()

        if args.O:
            # Print result
            controller.output_result(result)

        # Check if we need to write to file
        if write_file is not None:
            controller.output_result_file(result, write_file)
    else:
        # Incorrect usage of program
        argparser.error("Incorrect Usage. Correct usage 'python runner.py <domain.suffix> <problem.suffix>'")
