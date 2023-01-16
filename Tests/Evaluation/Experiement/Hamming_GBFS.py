import itertools
import re
import time
import os
from math import comb
from runner import Runner
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder


def run_test(domain_file_path, problem_file_path):
    # TODO: Find Amount of Steps to hit 5 mins
    controller = Runner(domain_file_path, problem_file_path)
    controller.set_search_queue(GBFSSearchQueue)
    controller.set_heuristic(HammingDistancePartialOrder)
    controller.parse_domain()
    controller.parse_problem()

    # Start Search
    controller.solver.solve(search=False)
    num_expansions = 0
    res = None
    while num_expansions < 1000000 and not res:
        res = controller.solver._search(True)
        num_expansions += 1

    if res:
        # Get Solve Time
        controller = Runner(domain_file_path, problem_file_path)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(HammingDistancePartialOrder)
        controller.parse_domain()
        controller.parse_problem()

        start_time = time.time()
        controller.solve()
        end_time = time.time()
        solve_time = end_time - start_time

        # Find the percentage of facts in the final state
        all_possible_facts, total_possible_pairs, total_actual_pairs = \
            calculate_all_possible_facts_and_pairings(controller.domain, controller.problem, res)
        percentage_facts = (len(res.current_state.elements) / len(all_possible_facts)) * 100
        percentage_pairs = (total_actual_pairs / total_possible_pairs) * 100

        # Write to file
        problem_file_path_slashes = [i.start() for i in re.finditer('/', problem_file_path)]
        write_to_file(problem_file_path[problem_file_path_slashes[-2] + 1:], num_expansions, solve_time, percentage_facts, percentage_pairs)
    else:
        raise NotImplementedError


def calculate_all_possible_facts_and_pairings(domain, problem, model):
    # For each predicate in the domain
    possible_facts = []
    total_possible_pairs = 0
    total_actual_pairs = 0
    for predicate in domain.predicates:
        predicate = domain.get_predicate(predicate)
        parameter_options = []

        # For each parameter get a list of possible objects
        for param in predicate.parameters:
            parameter_options.append(problem.get_objects_of_type(param.type))

        # Use itertools to get all combinations
        all_param_combinations = list(itertools.product(*parameter_options))
        predicate_all_combinations = []
        for combination in all_param_combinations:
            predicate_all_combinations.append(ProblemPredicate(predicate, list(combination)))

        # TODO: Consider pairs here
        possible_pairs = comb(len(predicate_all_combinations), 2)
        actual_predicate_indexes = model.get_state().get_indexes(predicate.name)

        if actual_predicate_indexes:
            num_actual_occurrence_of_predicate = len(actual_predicate_indexes)
        else:
            num_actual_occurrence_of_predicate = 0

        actual_pairs = comb(num_actual_occurrence_of_predicate, 2)
        total_possible_pairs += possible_pairs
        total_actual_pairs += actual_pairs

        possible_facts += predicate_all_combinations

    # Return all possible facts
    return possible_facts, total_possible_pairs, total_actual_pairs


def write_to_file(problem_name, number_expansions, solve_time, percentage_facts, percentage_pairs):
    file_name = 'results.csv'
    if os.path.exists(file_name):
        # If file exists open it and append
        write_file = open(file_name, 'a')
    else:
        # If file does not exist make one
        write_file = open(file_name, 'w')
        write_file.write('Problem,number expansions,solve time,percentage facts,percentage pairs')
    write_file.write("\n{},{},{},{},{}".format(problem_name, number_expansions, solve_time, percentage_facts, percentage_pairs))
    write_file.close()


if __name__ == "__main__":
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl")
