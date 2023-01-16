import itertools
from math import comb
from runner import Runner
from Internal_Representation.problem_predicate import ProblemPredicate
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder


def run_test(domain_file_path, problem_file_path):
    # TODO: Find Amount of Steps to hit 5 mins
    # TODO: Percentage of facts in the final state
    # TODO: Percentage of pairs of facts reached
    # TODO: Get time to find solution
    controller = Runner(domain_file_path, problem_file_path)
    controller.set_search_queue(GBFSSearchQueue)
    controller.set_heuristic(HammingDistancePartialOrder)
    controller.parse_domain()
    controller.parse_problem()

    # Start Search
    controller.solver.solve(search=False)
    num_expansions = 0
    res = None
    while num_expansions < 100000000 and not res:
        res = controller.solver._search(True)
        num_expansions += 1

    if res:
        # Find the percentage of facts in the final state
        all_possible_facts = calculate_all_possible_facts_and_pairings(controller.domain, controller.problem, res)
        precentage_facts = (len(res.current_state.elements) / len(all_possible_facts)) * 100
        raise NotImplementedError
    else:
        raise NotImplementedError


def calculate_all_possible_facts_and_pairings(domain, problem, model):
    # For each predicate in the domain
    possible_facts = []
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
        num_actual_occurence_of_predicate = len(model.get_state().get_indexes(predicate.name))
        actual_pairs = comb(num_actual_occurence_of_predicate, 2)
        print('here')

        possible_facts += predicate_all_combinations

    # Return all possible facts
    return possible_facts

if __name__ == "__main__":
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl")
