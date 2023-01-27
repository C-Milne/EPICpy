import itertools
import re
import time
import os
import sys
from math import comb
working_dir = os.getcwd()
os.chdir("../../..")
sys.path.append(os.getcwd())
os.chdir(working_dir)
from runner import Runner
from Solver.Models.model import Model
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Search_Queues.Novelty_TreeDistance_GBFS_Search_Queue import NoveltyTreeDistanceGBFSSearchQueue
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Heuristics.no_pruning import NoPruning
from Solver.Heuristics.pruning import Pruning
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Heuristics.hamming_distance_seen_states import HammingDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance_seen_states import TreeDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver


def run_test(domain_file_path, problem_file_path):
    Model.model_counter = 0
    print(domain_file_path)
    print(problem_file_path)
    controller = Runner(domain_file_path, problem_file_path)

    # controller.set_solver(PartialOrderNoveltySolver)

    # controller.set_search_queue(GBFSSearchQueue)
    # controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)

    # controller.set_heuristic(TreeDistanceSeenStatesPruning)
    controller.set_heuristic(SeenStatesPruning)

    controller.parse_domain()
    controller.parse_problem()

    # Start Search
    controller.solver.solve(search=False)
    start_time = time.time()
    res = controller.solver._search()
    end_time = time.time()
    solve_time = end_time - start_time
    models_created = res.model_counter

    # Write to file
    problem_file_path_slashes = [i.start() for i in re.finditer('/', problem_file_path)]
    write_to_file(problem_file_path[problem_file_path_slashes[-2] + 1:], solve_time, models_created)


def write_to_file(problem_name, solve_time, models_created):
    file_name = 'performance-evaluation-results.csv'
    if os.path.exists(file_name):
        # If file exists open it and append
        write_file = open(file_name, 'a')
    else:
        # If file does not exist make one
        write_file = open(file_name, 'w')
        write_file.write('Problem,solve time,models created')
    write_file.write("\n{},{},{}".format(problem_name, solve_time, models_created))
    write_file.close()


if __name__ == "__main__":
    """Rover Problems"""
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p02.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p03.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p04.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p05.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p06.hddl")
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p07.hddl")
    """Barman Problems"""
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile01.hddl")
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile02.hddl")
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile03.hddl")
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile04.hddl")
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile05.hddl")
    # run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile06.hddl")
    """Depots Problems"""
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p01.hddl")
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p02.hddl")
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p03.hddl")
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p04.hddl")
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p05.hddl")
    # run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p06.hddl")
    """Factories Problems"""
    # run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile01.hddl")
    # run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile02.hddl")
    # run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile03.hddl")
    # run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile04.hddl")

