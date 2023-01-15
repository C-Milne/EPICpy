import os
import shutil
import sys
import time
import pickle
import re

working_dir = os.getcwd()
os.chdir("../../..")
sys.path.append(os.getcwd())
from Solver.Search_Queues.search_queue import SearchQueue
from runner import Runner
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Solver.Solving_Algorithms.total_order import TotalOrderSolver
from Solver.Models.default_model import DefaultModel
os.chdir(working_dir)

"""Methods for Operation"""


class Strat:
    def __init__(self, name, class_reference, early_task_precon_checker=True):
        self.name = name
        self.class_reference = class_reference
        self.file = None
        self.early_task_precon_checker = early_task_precon_checker


def create_file(strat):
    # Check which files are already made
    # Do not overwrite any existing files
    file_name = strat.name + ".csv"
    counter = 0
    while os.path.exists(file_name):
        counter += 1
        file_name = strat.name + str(counter) + ".csv"

    # Create file
    strat.file = open(file_name, "w")
    strat.file.write("example_name,time_taken,search_models_created,serialised_actions_taken,serialised_state")


def save_to_file(test_name, strat, time, result):
    print("Writing: {}".format(time))
    # Pickle actions taken and state. Save them in the /serialised_objects folder
    pickle_test_name = test_name.replace("/", "_") + "_" + strat.name

    if result is not None:
        actions_taken_pickle_file = save_pickle_object(result.actions_taken, pickle_test_name + "_" + "actions")
        state_pickle_file = save_pickle_object(result.current_state, pickle_test_name + "_" + "state")
        num_models = result.num_models_used
    else:
        actions_taken_pickle_file, state_pickle_file = "NONE", "NONE"
        num_models = 0

    strat.file.write("\n" + test_name + "," + str(time) + "," + str(num_models) + "," + actions_taken_pickle_file + "," +
                     state_pickle_file)


def save_pickle_object(object, file_name) -> str:
    file_name = file_name.replace(".", "")
    # Find a suitable file name
    f_name = "serialised_objects\\" + file_name + ".pickle"
    counter = 0
    while os.path.exists(f_name):
        counter += 1
        f_name = "serialised_objects\\" + file_name + str(counter) + ".pickle"

    # Save pickle file
    file = open(f_name, "wb")
    file.write(pickle.dumps(object))
    file.close()

    # Return file name
    return f_name


def test_runner(test, heuristic, early_precon, partial_order, search, search_queue):
    controller = Runner(test[0], test[1])

    result = [_.start() for _ in re.finditer("/", test[1])]
    test_name = test[1][result[-2] + 1:]

    if search:
        controller.parse_domain()
        controller.parse_problem()
    else:
        # If we are not timing the search we are timing the parsing
        start_time = time.time()
        controller.parse_domain()
        controller.parse_problem()
        end_time = time.time()
        timeTaken = end_time - start_time
        save_to_file(test_name, heuristic, timeTaken, None)
        return

    if partial_order:
        controller.set_solver(PartialOrderSolver)
    else:
        controller.set_solver(TotalOrderSolver)

    controller.set_search_queue(search_queue)

    controller.set_heuristic(heuristic.class_reference)
    controller.solver.task_expansion_given_param_check = early_precon
    DefaultModel.model_counter = 0   # This needs to be reset for each test

    start_time = time.time()
    res = controller.solve()
    end_time = time.time()

    assert res is not None

    timeTaken = end_time - start_time

    save_to_file(test_name, heuristic, timeTaken, res)


def run_tests(tests, strats, sub_folder, clear_folder=False, **kwargs):
    os.chdir("Archive")
    # Clear subfolder
    if clear_folder:
        if os.path.isdir(sub_folder):
            shutil.rmtree(sub_folder)
    if not os.path.isdir(sub_folder):
        os.mkdir(sub_folder)
        os.mkdir(sub_folder + "/serialised_objects")
    os.chdir(sub_folder)

    if "early_precon" in kwargs.keys():
        early_precon = kwargs["early_precon"]
        assert type(early_precon) == bool
    else:
        early_precon = True

    if 'search' in kwargs.keys():
        run_search = kwargs['search']
        assert type(run_search) == bool
    else:
        run_search = True

    if 'SearchQueue' in kwargs.keys():
        search_queue = kwargs['SearchQueue']
    else:
        search_queue = SearchQueue

    # Create log csv for each strategy being assessed
    for s in strats:
        create_file(s)
    for t in tests:
        for s in strats:
            for i in range(5):
                if 'partial_order' in kwargs:
                    partial_order = kwargs['partial_order']
                else:
                    partial_order = False
                test_runner(t, s, early_precon, partial_order, run_search, search_queue)
    for s in strats:
        s.file.close()
    os.chdir("../..")

if __name__ == "__main__":
    """##################################################################################################################"""
    """Test Rover p01 -> p03 with breadth first search without pruning (No early precon checking) -> DONE"""
    # tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl")]
    #
    # strats = [Strat("Breadth_First_Operations", BreadthFirstOperations, False)]
    #
    # run_tests(tests, strats, "Rover_no_early_precon", True, early_precon=False)

    """Test Rover p01 -> p04 with breadth first search and pruning (No early precon checking) -> DONE"""
    # tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl")]
    #
    # strats = [Strat("Breadth_First_Operations_Pruning", BreadthFirstOperationsPruning, False)]
    # run_tests(tests, strats, "Rover_no_early_precon", False, early_precon=False)

    """##################################################################################################################"""
    """TEST TOTAL ORDERED PROBLEM WITH PARTIAL ORDER SOLVER AND TOTAL ORDER SOLVER (ROVER 1 -> 4)"""
    """Partial Order -> Done"""
    # tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl")]
    #
    # strats = [Strat("Breadth_First_Operations_Pruning_PO", BreadthFirstOperationsPruning)]
    #
    # run_tests(tests, strats, "Rover_PO_TO", True, partial_order=True)

    """Total Order -> Done"""
    # tests = [("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p01.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p02.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p03.hddl"),
    # ("../../../../Examples/Rover/domain.hddl", "../../../../Examples/Rover/p04.hddl")]
    #
    # strats = [Strat("Breadth_First_Operations_Pruning_TO", BreadthFirstOperationsPruning)]
    #
    # run_tests(tests, strats, "Rover_PO_TO")
