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
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder


def run_test(domain_file_path, problem_file_path):
    controller = Runner(domain_file_path, problem_file_path)
    controller.set_search_queue(GBFSSearchQueue)
    controller.set_heuristic(HammingDistancePartialOrder)
    controller.parse_domain()
    controller.parse_problem()

    # Start Search
    controller.solver.solve(search=False)
    num_expansions = 0
    res = None
    start_time = time.time()
    while time.time() - start_time < 300 and not res:    # while time.time() - start_time < 305
        res = controller.solver._search(True)
        num_expansions += 1
    end_time = time.time()
    solve_time = end_time - start_time

    solved = True
    if not res:
        # Find the model with the most operations
        solved = False
        models = controller.solver.search_models._Q
        res = models[0]
        for m in models[1:]:
            if m.get_num_operations_taken() > res.get_num_operations_taken():
                res = m

    # Find the percentage of facts in the final state
    all_possible_facts, total_possible_pairs, total_actual_pairs = \
        calculate_all_possible_facts_and_pairings(controller.domain, controller.problem, res)
    percentage_facts = (len(res.current_state.elements) / len(all_possible_facts)) * 100
    percentage_pairs = (total_actual_pairs / total_possible_pairs) * 100

    # Write to file
    problem_file_path_slashes = [i.start() for i in re.finditer('/', problem_file_path)]
    write_to_file(problem_file_path[problem_file_path_slashes[-2] + 1:], num_expansions, solve_time, percentage_facts, percentage_pairs, solved)



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


def write_to_file(problem_name, number_expansions, solve_time, percentage_facts, percentage_pairs, solved):
    file_name = 'results.csv'
    if os.path.exists(file_name):
        # If file exists open it and append
        write_file = open(file_name, 'a')
    else:
        # If file does not exist make one
        write_file = open(file_name, 'w')
        write_file.write('Problem,number expansions,solve time,percentage facts,percentage pairs,Solved')
    write_file.write("\n{},{},{},{},{},{}".format(problem_name, number_expansions, solve_time, percentage_facts, percentage_pairs, solved))
    write_file.close()


if __name__ == "__main__":
    """Rover Problems"""
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p02.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p03.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p04.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p05.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p06.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p07.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p08.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p09.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p10.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p11.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p12.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p13.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p14.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p15.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p16.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p17.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p18.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p19.hddl")
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p20.hddl")
    """Barman Problems"""
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile01.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile02.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile03.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile04.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile05.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile06.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile07.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile08.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile09.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile10.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile11.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile12.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile13.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile14.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile15.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile16.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile17.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile18.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile19.hddl")
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile20.hddl")
    """Depots Problems"""
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p01.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p02.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p03.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p04.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p05.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p06.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p07.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p08.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p09.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p10.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p11.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p12.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p13.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p14.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p15.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p16.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p17.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p18.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p19.hddl")
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p20.hddl")
    """Factories Problems"""
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile01.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile02.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile03.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile04.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile05.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile06.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile07.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile08.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile09.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile10.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile11.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile12.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile13.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile14.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile15.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile16.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile17.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile18.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile19.hddl")
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile20.hddl")
