import itertools
import re
import time
import os
import subprocess
import sys
from datetime import datetime
import argparse
from math import comb

working_dir = os.getcwd()
os.chdir("../../..")
sys.path.append(os.getcwd())
os.chdir(working_dir)
from runner import Runner
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.state_novelty import StateNovelty
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Search_Queues.Greedy_Best_First_Search_Queue_Newest_First import GBFSSearchQueueNewestFirst
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Search_Queues.Novelty_GBFS_Search_Queue_Oldest_First import NoveltyGBFSOldestFirstQueue
from Solver.Search_Queues.Novelty_TreeDistance_GBFS_Search_Queue import NoveltyTreeDistanceGBFSSearchQueue
from Solver.Search_Queues.search_queue_dual_heuristic_HammingDistance import SearchQueueGBFSDualHammingDistance
from Solver.Search_Queues.search_queue_dual_heuristic_TreeDistance import SearchQueueGBFSDualTreeDistance
from Solver.Search_Queues.search_queue_dual_heuristic_Landmarks import SearchQueueGBFSDualLandmarks
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Heuristics.no_pruning import NoPruning
from Solver.Heuristics.hamming_distance_seen_states import HammingDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance_seen_states import TreeDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Heuristics.landmarks import Landmarks
from Solver.Heuristics.landmarks_no_reachability import LandmarksNoReachability
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Solver.Solving_Algorithms.partial_order_novelty_light import PartialOrderNoveltyLightSolver
from Solver.Solving_Algorithms.partial_order_novelty_no_reset import PartialOrderNoveltyNoResetSolver
from Solver.Solving_Algorithms.partial_order_novelty_level_2 import PartialOrderNoveltyLevelTwoSolver
from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver
from Solver.Solving_Algorithms.partial_order_novelty_methods_only import PartialOrderNoveltyMethodsOnlySolver
from Solver.Solving_Algorithms.partial_order_novelty_methods_no_reset import PartialOrderNoveltyMethodsNoResetSolver
from Solver.Solving_Algorithms.partial_order_novelty_methods_tasks import PartialOrderNoveltyMethodsTasksSolver
from Solver.Solving_Algorithms.partial_order_novelty_level_2_no_reset import PartialOrderNoveltyLevelTwoNoResetSolver
from Solver.Solving_Algorithms.partial_order_hamming_novelty import PartialOrderHammingNoveltySolver
from Solver.Solving_Algorithms.partial_order_hamming_novelty_no_reset import PartialOrderHammingNoveltyNoResetSolver
from Solver.Models.PandaVerifyModel import PandaVerifyModel
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker

PANDAVERIFYSUCCESSFULLOUTPUT = "IDs of subtasks used in the plan exist: trueTasks declared in plan actually exist and " \
                               "can be instantiated as given: trueMethods don't contain duplicate subtasks: " \
                               "trueMethods don't contain orphaned " \
                               "tasks: trueMethods can be instantiated: trueOrder induced by methods is present in " \
                               "plan: truePlan is executable: " \
                               "truePlan verification result: true"


def run_test(domain_file_path, problem_file_path, strategy):
    print(domain_file_path)
    print(problem_file_path)
    controller = Runner(domain_file_path, problem_file_path)

    if strategy == 1:
        """Hamming Distance (Seen States)"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Distance-seen-states-results.csv'
    elif strategy == 2:
        """Seen States Pruning"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(SeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/seen-state-breadth-first-results.csv'
    elif strategy == 3:
        """Tree Distance (Seen States)"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Tree-Distance-seen-states-results.csv'
    elif strategy == 4:
        """Novelty - Level 1 - Reset to 0 after task or method expansion"""
        controller.set_solver(PartialOrderNoveltySolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_reset-newest-results.csv'
    elif strategy == 5:
        """Tree Distance"""
        # controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(TreeDistance)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Tree-Distance-results.csv'
    elif strategy == 6:
        """Novelty - Level 1 - Reset to 0 after task or method expansion - Tree Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltySolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_reset-TreeDis-results.csv'
    elif strategy == 7:
        """Tree Distance (Seen States) - Newest First Search Queue"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueueNewestFirst)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Tree-Distance-seen-states-newest-first-results.csv'
    elif strategy == 8:
        """Hamming Distance (Seen States) - Newest First Search Queue"""
        # controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueueNewestFirst)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Distance-seen-states-newest-first-results.csv'
    elif strategy == 9:
        """Tree Distance with Hamming Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualHammingDistance)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Tree-Distance-seen-states-Hamming-Distance-tie-breaker-results.csv'
    elif strategy == 10:
        """Novelty - Level 1 - No reset after task or method expansion"""
        controller.set_solver(PartialOrderNoveltyNoResetSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_No-Reset-results.csv'
    elif strategy == 11:
        """Novelty - Level 2 - Reset after task or method expansion"""
        controller.set_solver(PartialOrderNoveltyLevelTwoSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_level2_reset-results.csv'
    elif strategy == 12:
        """Novelty - level1 - Checking for Novel Method"""
        controller.set_solver(PartialOrderNoveltyMethodsSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Methods-results.csv'
    elif strategy == 13:
        """Novelty - Level 1 - Reset to 0 after task or method expansion - oldest first"""
        controller.set_solver(PartialOrderNoveltySolver)
        controller.set_search_queue(NoveltyGBFSOldestFirstQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_reset-Oldest-First-results.csv'
    elif strategy == 14:
        """Landmarks"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Landmarks-results.csv'
    elif strategy == 15:
        """Novelty - Level 1 - Reset to 0 after task or method expansion - Hamming Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltySolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_reset-HamDis-results.csv'
    elif strategy == 16:
        """Novelty - Level 2 - No reset after task or method expansion"""
        controller.set_solver(PartialOrderNoveltyLevelTwoNoResetSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_level2_no_reset-results.csv'
    elif strategy == 17:
        """Novelty - level1 - Checking for Novel Method - Oldest First"""
        controller.set_solver(PartialOrderNoveltyMethodsSolver)
        controller.set_search_queue(NoveltyGBFSOldestFirstQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Methods_oldest_first-results.csv'
    elif strategy == 18:
        """Novelty - Level 1 - No Reset to 0 after task or method expansion - Tree Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyNoResetSolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_no_reset-TreeDis-results.csv'
    elif strategy == 19:
        """Novelty - Level 1 - No Reset to 0 after task or method expansion - Hamming Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyNoResetSolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_no_reset-HamDis-results.csv'
    elif strategy == 20:
        """Novelty - Level 1 - Reset to 0 after task or method expansion - Landmarks Tie Breaker"""
        controller.set_solver(PartialOrderNoveltySolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_reset-Landmarks-results.csv'
    elif strategy == 21:
        """Novelty - Level 1 - No Reset to 0 after task or method expansion - Landmarks Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyNoResetSolver)
        controller.set_search_queue(NoveltyTreeDistanceGBFSSearchQueue)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Only_no_reset-Landmarks-results.csv'
    elif strategy == 22:
        """Landmarks with Hamming Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualHammingDistance)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Landmarks-Hamming-Distance-tie-breaker-results.csv'
    elif strategy == 23:
        """Landmarks with Tree Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualTreeDistance)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Landmarks-Tree-Distance-tie-breaker-results.csv'
    elif strategy == 24:
        """Landmarks - Newest First Search Queue"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueueNewestFirst)
        controller.set_heuristic(Landmarks)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Landmarks-newest-first-results.csv'
    elif strategy == 25:
        """Hamming Distance with Tree Distance Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualTreeDistance)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Distance-seen-states-Tree-Distance-tie-breaker-results.csv'
    elif strategy == 26:
        """Tree Distance with Landmarks Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualLandmarks)
        controller.set_heuristic(TreeDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Tree-Distance-seen-states-landmarks-tie-breaker-results.csv'
    elif strategy == 27:
        """Hamming Distance with Landmarks Tie Breaker"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(SearchQueueGBFSDualLandmarks)
        controller.set_heuristic(HammingDistanceSeenStatesPruning)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Distance-seen-states-landmarks-tie-breaker-results.csv'
    elif strategy == 28:
        """Novelty - level1 - Checking for Novel Methods and Tasks"""
        controller.set_solver(PartialOrderNoveltyMethodsTasksSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Methods_Tasks-results.csv'
    elif strategy == 29:
        """Novelty - level1 - Checking for Novel Methods and Tasks - Oldest First"""
        controller.set_solver(PartialOrderNoveltyMethodsTasksSolver)
        controller.set_search_queue(NoveltyGBFSOldestFirstQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Methods_Tasks_oldest_first-results.csv'
    elif strategy == 30:
        """Hamming Distance with Novelty Tie Breaker - Reset - Newest First"""
        controller.set_solver(PartialOrderHammingNoveltySolver)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Novelty-Reset-Newest.csv'
    elif strategy == 31:
        """Hamming Distance with Novelty Tie Breaker - No Reset - Newest First"""
        controller.set_solver(PartialOrderHammingNoveltyNoResetSolver)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Hamming-Novelty-No-Reset-Newest.csv'
    elif strategy == 32:
        """Novelty - level1 - Checking for Novel Method - No Reset"""
        controller.set_solver(PartialOrderNoveltyMethodsNoResetSolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Facts_Methods_No_Reset-results.csv'
    elif strategy == 33:
        """Novelty - Checking for Novel Method - ONLY - Newest First"""
        controller.set_solver(PartialOrderNoveltyMethodsOnlySolver)
        controller.set_search_queue(NoveltyGBFSQueue)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Novelty_Methods_Only_Reset_Newest-results.csv'
    elif strategy == 34:
        """Landmarks - No Reachability"""
        controller.set_solver(PartialOrderNoveltyLightSolver)
        controller.set_search_queue(GBFSSearchQueue)
        controller.set_heuristic(LandmarksNoReachability)
        controller.set_model(PandaVerifyModel)
        controller.set_progress_tracker(PandaVerifyFormatTracker)
        file_name = 'results/Landmarks_No_Reachability-results.csv'
    else:
        raise ValueError('Unknown strategy code: {}'.format(strategy))

    controller.parse_domain()
    controller.parse_problem()

    # Start Search
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    setup_start_time = time.time()
    controller.solver.solve(search=False)
    setup_end_time = time.time()
    setup_time = setup_end_time - setup_start_time
    num_expansions = 0
    res = None
    solve_start_time = time.time()
    while time.time() - solve_start_time < 10000 and not res:
        res = controller.solver._search(True)
        num_expansions += 1
    solve_end_time = time.time()
    solve_time = solve_end_time - solve_start_time

    solved = True
    if not res:
        # Find the model with the most operations
        solved = False
        models = controller.solver.search_models.get_model_list()
        if len(models) > 0:
            res = models[0]
            for m in models[1:]:
                if m.get_num_operations_taken() > res.get_num_operations_taken():
                    res = m
        else:
            res = None

    # Find the percentage of facts in the final state
    all_possible_facts, total_possible_pairs, total_actual_pairs = \
        calculate_all_possible_facts_and_pairings(controller.domain, controller.problem, res)
    if res is not None:
        percentage_facts = (len(res.current_state.elements) / len(all_possible_facts)) * 100
        percentage_pairs = (total_actual_pairs / total_possible_pairs) * 100
    else:
        percentage_facts = 'N/A'
        percentage_pairs = 'N/A'

    # Find percentage of novel states
    if isinstance(controller.solver, PartialOrderNoveltySolver):
        num_novel_states = controller.solver.num_novel_states
        num_not_novel_states = controller.solver.num_not_novel_states
        if num_novel_states + num_not_novel_states == 0:
            percentage_novel_states = 0
        else:
            percentage_novel_states = (num_novel_states / (num_novel_states + num_not_novel_states)) * 100
        new_state = StateNovelty()
        num_unique_facts = len(new_state.seen_elements)
        num_novel_methods = controller.solver.num_novel_methods
        num_not_novel_methods = controller.solver.num_not_novel_methods
    else:
        num_novel_states = 'N/A'
        num_not_novel_states = 'N/A'
        percentage_novel_states = 'N/A'
        num_unique_facts = 'N/A'
        num_novel_methods = 'N/A'
        num_not_novel_methods = 'N/A'

    if res is not None:
        model_elements = len(res.current_state.elements)
    else:
        model_elements = 'N/A'

    # Find number of novel methods with novel states
    if isinstance(controller.solver, PartialOrderNoveltyMethodsNoResetSolver) or \
            isinstance(controller.solver, PartialOrderHammingNoveltyNoResetSolver):
        num_novel_method_not_novel_state = controller.solver.num_novel_method_not_novel_state
        num_novel_methods_novel_state = controller.solver.num_novel_methods_novel_state
    else:
        num_novel_method_not_novel_state = 'N/A'
        num_novel_methods_novel_state = 'N/A'

    if res is not None and isinstance(res, PandaVerifyModel) and \
            isinstance(res.progress_tracker, PandaVerifyFormatTracker) and sys.platform != "win32":
        output_file_name = "{}.txt".format(strategy)
        controller.output_result_file(res, output_file_name)
        # print('OUTPUT FILE NAME: {}'.format(output_file_name))
        # print('VERIFYING')
        result = subprocess.run(
            './pandaPIparser -C --verify {} {} output/{}'.format(domain_file_path, problem_file_path, output_file_name),
            shell=True, capture_output=True, text=True)

        output = ''.join(s for s in str(result.stdout) if 31 < ord(s) < 126)

        if PANDAVERIFYSUCCESSFULLOUTPUT in output:
            verified = True
        else:
            verified = False
        # print('VERIFIED: {}'.format(verified))
    else:
        verified = 'N/A'

    # Write to file
    problem_file_path_slashes = [i.start() for i in re.finditer('/', problem_file_path)]
    problem_file_name = problem_file_path[problem_file_path_slashes[-2] + 1:]

    write_to_file(problem_file_name, num_expansions, solve_time, setup_time,
                  len(all_possible_facts), model_elements, percentage_facts,
                  total_possible_pairs, total_actual_pairs, percentage_pairs,
                  num_novel_states, num_not_novel_states, percentage_novel_states,
                  num_unique_facts, num_novel_methods, num_not_novel_methods,
                  num_novel_method_not_novel_state, num_novel_methods_novel_state,
                  solved, verified, file_name)


def calculate_all_possible_facts_and_pairings(domain, problem, model):
    # For each predicate in the domain
    possible_facts = []
    total_possible_pairs = 0
    total_actual_pairs = 0
    for predicate in domain.predicates:
        predicate = domain.get_predicate(predicate)
        parameter_options = []

        # For each parameter get a list of possible objects
        if predicate.parameters:
            for param in predicate.parameters:
                valid_obs = []
                param_type = param.type
                for ob in problem.get_all_objects():
                    ob = problem.get_object(ob)
                    type_satisfied = ParameterSelector.check_satisfies_type(param_type, ob)
                    if type_satisfied:
                        valid_obs.append(ob)
                parameter_options.append(valid_obs)
        else:
            parameter_options.append([])

        # Use itertools to get all combinations
        all_param_combinations = list(itertools.product(*parameter_options))
        predicate_all_combinations = []
        for combination in all_param_combinations:
            predicate_all_combinations.append(ProblemPredicate(predicate, list(combination)))

        possible_facts += predicate_all_combinations

    # Now calculate all possible pairs
    total_possible_pairs = comb(len(possible_facts), 2)
    if model is not None:
        total_actual_pairs = comb(len(model.current_state.elements), 2)
    else:
        total_actual_pairs = 'N/A'

    # Return all possible facts
    return possible_facts, total_possible_pairs, total_actual_pairs


def write_to_file(problem_name, number_expansions, solve_time, setup_time,
                  all_possible_facts, actual_facts, percentage_facts,
                  total_possible_pairs, total_actual_pairs, percentage_pairs,
                  num_novel_states, num_not_novel_states, percentage_novel_states,
                  num_unique_facts,
                  num_novel_methods, num_not_novel_methods,
                  num_novel_method_not_novel_state, num_novel_methods_novel_state,
                  solved, verified, file_name):
    if os.path.exists(file_name):
        # If file exists open it and append
        write_file = open(file_name, 'a')
    else:
        if '/' in file_name:
            target_folder = file_name.split('/')[0]
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)
        # If file does not exist make one
        write_file = open(file_name, 'w')
        write_file.write(
            'Problem,number_expansions,solve_time,setup_time,' +
            'all_facts,actual_facts,percentage_facts,possible_pairs,' +
            'actual_pairs,percentage_pairs,' +
            'num_novel_states,num_not_novel_states,percentage_novel_states,' +
            'num_unique_facts,' +
            'num_novel_methods,num_not_novel_methods,' +
            'num_novel_method_not_novel_state,num_novel_methods_novel_state,' +
            'Verified,Solved')
    write_file.write(
        "\n{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(problem_name, number_expansions,
                                                                               solve_time, setup_time,
                                                                               all_possible_facts,
                                                                               actual_facts, percentage_facts,
                                                                               total_possible_pairs,
                                                                               total_actual_pairs,
                                                                               percentage_pairs,
                                                                               num_novel_states,
                                                                               num_not_novel_states,
                                                                               percentage_novel_states,
                                                                               num_unique_facts,
                                                                               num_novel_methods,
                                                                               num_not_novel_methods,
                                                                               num_novel_method_not_novel_state,
                                                                               num_novel_methods_novel_state,
                                                                               str(verified), solved))
    write_file.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("strategy", metavar='S', type=int, nargs="?",
                           help='Number corresponding to strategy required',
                           default=None)
    args = argparser.parse_args()
    strategy = args.strategy

    if strategy is None:
        argparser.error("Incorrect Usage. Strategy MUST be set!")

    # Rover Problems
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl", strategy)
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl", strategy)
    # run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p01.hddl", strategy)

    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p02.hddl", strategy)
    """
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p02.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p03.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p04.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p05.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p06.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p07.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p08.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p09.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p10.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p11.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p12.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p13.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p14.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p15.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p16.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p17.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p18.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p19.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p20.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p21.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p22.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p23.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p24.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p25.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p26.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p27.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p28.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p29.hddl", strategy)
    run_test("../../Examples/Rover/domain.hddl", "../../Examples/Rover/p30.hddl", strategy)
    # Barman Problems
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile01.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile02.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile03.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile04.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile05.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile06.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile07.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile08.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile09.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile10.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile11.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile12.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile13.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile14.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile15.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile16.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile17.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile18.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile19.hddl", strategy)
    run_test("../../Examples/Barman/domain.hddl", "../../Examples/Barman/pfile20.hddl", strategy)
    # Depots Problems
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p01.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p02.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p03.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p04.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p05.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p06.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p07.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p08.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p09.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p10.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p11.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p12.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p13.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p14.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p15.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p16.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p17.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p18.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p19.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p20.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p21.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p22.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p23.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p24.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p25.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p26.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p27.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p28.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p29.hddl", strategy)
    run_test("../../Examples/Depots/domain.hddl", "../../Examples/Depots/p30.hddl", strategy)
    # Factories Problems
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile01.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile02.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile03.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile04.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile05.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile06.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile07.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile08.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile09.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile10.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile11.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile12.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile13.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile14.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile15.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile16.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile17.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile18.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile19.hddl", strategy)
    run_test("../../Examples/Factories/domain.hddl", "../../Examples/Factories/pfile20.hddl", strategy)
    # Assembly Problems
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth01.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth02.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth03.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth04.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth05.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth06.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth07.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth08.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth09.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth10.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth11.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth12.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth13.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth14.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth15.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth16.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth17.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth18.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth19.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth20.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth21.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth22.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth23.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth24.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth25.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth26.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth27.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth28.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth29.hddl", strategy)
    run_test("../../Examples/AssemblyHierarchical/domain.hddl", "../../Examples/AssemblyHierarchical/genericLinearProblem_depth30.hddl", strategy)
    # BlocksWorld Problems
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p01.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p02.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p03.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p04.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p05.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p06.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p07.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p08.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p09.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p10.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p11.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p12.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p13.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p14.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p15.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p16.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p17.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p18.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p19.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p20.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p21.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p22.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p23.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p24.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p25.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p26.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p27.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p28.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p29.hddl", strategy)
    run_test("../../Examples/Blocksworld-GTOHP/domain.hddl", "../../Examples/Blocksworld-GTOHP/p30.hddl", strategy)
    # Childsnack Problems
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p01.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p02.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p03.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p04.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p05.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p06.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p07.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p08.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p09.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p10.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p11.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p12.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p13.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p14.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p15.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p16.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p17.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p18.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p19.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p20.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p21.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p22.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p23.hddl", strategy)
    run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p24.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p25.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p26.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p27.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p28.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p29.hddl", strategy)
    # run_test("../../Examples/Childsnack/domain.hddl", "../../Examples/Childsnack/p30.hddl", strategy)
    # Elevator Problems
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s01-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s01-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s02-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s02-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s02-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s02-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s02-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s03-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s03-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s03-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s03-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s03-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s04-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s04-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s04-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s04-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s04-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s05-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s05-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s05-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s05-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s05-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s06-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s06-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s06-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s06-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s06-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s07-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s07-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s07-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s07-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s07-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s08-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s08-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s08-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s08-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s08-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s09-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s09-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s09-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s09-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s09-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s10-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s10-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s10-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s10-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s10-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s11-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s11-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s11-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s11-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s11-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s12-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s12-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s12-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s12-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s12-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s13-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s13-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s13-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s13-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s13-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s14-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s14-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s14-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s14-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s14-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s15-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s15-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s15-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s15-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s15-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s16-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s16-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s16-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s16-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s16-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s17-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s17-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s17-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s17-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s17-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s18-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s18-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s18-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s18-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s18-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s19-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s19-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s19-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s19-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s19-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s20-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s20-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s20-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s20-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s20-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s21-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s21-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s21-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s21-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s21-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s22-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s22-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s22-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s22-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s22-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s23-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s23-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s23-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s23-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s23-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s24-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s24-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s24-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s24-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s24-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s25-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s25-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s25-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s25-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s25-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s26-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s26-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s26-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s26-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s26-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s27-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s27-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s27-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s27-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s27-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s28-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s28-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s28-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s28-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s28-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s29-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s29-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s29-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s29-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s29-4.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s30-0.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s30-1.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s30-2.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s30-3.hddl", strategy)
    run_test("../../Examples/Elevator-Learned-ECAI-16/domain.hddl", "../../Examples/Elevator-Learned-ECAI-16/s30-4.hddl", strategy)
    # Entertainment Problems
    run_test("../../Examples/Entertainment/pfile01-domain.hddl", "../../Examples/Entertainment/pfile01.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile02-domain.hddl", "../../Examples/Entertainment/pfile02.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile03-domain.hddl", "../../Examples/Entertainment/pfile03.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile04-domain.hddl", "../../Examples/Entertainment/pfile04.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile05-domain.hddl", "../../Examples/Entertainment/pfile05.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile06-domain.hddl", "../../Examples/Entertainment/pfile06.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile07-domain.hddl", "../../Examples/Entertainment/pfile07.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile08-domain.hddl", "../../Examples/Entertainment/pfile08.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile09-domain.hddl", "../../Examples/Entertainment/pfile09.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile10-domain.hddl", "../../Examples/Entertainment/pfile10.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile11-domain.hddl", "../../Examples/Entertainment/pfile11.hddl", strategy)
    run_test("../../Examples/Entertainment/pfile12-domain.hddl", "../../Examples/Entertainment/pfile12.hddl", strategy)
    # Freecell Problems
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-02-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-02-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-02-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-02-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-02-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-03-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-03-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-03-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-03-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-03-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-04-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-04-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-04-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-04-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-04-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-05-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-05-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-05-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-05-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-05-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-06-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-06-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-06-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-06-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-06-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-07-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-07-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-07-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-07-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-07-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-08-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-08-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-08-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-08-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-08-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-09-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-09-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-09-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-09-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-09-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-10-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-10-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-10-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-10-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-10-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-11-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-11-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-11-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-11-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-11-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-12-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-12-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-12-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-12-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-12-5.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-13-1.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-13-2.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-13-3.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-13-4.hddl", strategy)
    run_test("../../Examples/Freecell-Learned-ECAI-16/domain.hddl", "../../Examples/Freecell-Learned-ECAI-16/probfreecell-13-5.hddl", strategy)
    # Hiking Problems
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p01.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p02.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p03.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p04.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p05.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p06.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p07.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p08.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p09.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p10.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p11.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p12.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p13.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p14.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p15.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p16.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p17.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p18.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p19.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p20.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p21.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p22.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p23.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p24.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p25.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p26.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p27.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p28.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p29.hddl", strategy)
    run_test("../../Examples/Hiking/domain.hddl", "../../Examples/Hiking/p30.hddl", strategy)
    # Logistics Problems
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-04-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-04-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-04-2.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-05-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-05-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-05-2.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-06-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-06-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-06-2.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-06-3.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-07-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-07-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-08-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-08-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-09-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-09-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-10-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-10-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-11-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-11-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-12-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-12-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-13-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-13-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-14-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-14-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-15-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-15-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-16-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-16-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-17-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-17-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-18-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-18-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-19-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-19-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-20-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-20-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-21-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-21-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-22-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-22-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-23-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-23-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-24-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-24-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-25-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-25-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-26-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-26-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-27-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-27-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-28-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-28-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-29-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-29-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-30-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-30-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-31-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-31-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-32-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-32-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-33-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-33-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-34-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-34-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-35-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-35-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-36-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-36-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-37-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-37-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-38-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-38-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-39-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-39-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-40-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-40-1.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-41-0.hddl", strategy)
    run_test("../../Examples/Logistics-Learned-ECAI-16/domain.hddl", "../../Examples/Logistics-Learned-ECAI-16/probLOGISTICS-41-1.hddl", strategy)
    # Minecraft Player Problems
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-003-003-003.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-003-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-004-003-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-004-004-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-004-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-003-005-005-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-004-004-004-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-004-004-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-004-005-004-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-004-005-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-005-005-005-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-005-005-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-006-006-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-007-007-007-007.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-008-008-008-008.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-009-009-009-009.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-010-010-010-010.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-011-011-011-011.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-012-012-012-012.hddl", strategy)
    # run_test("../../Examples/Minecraft-Player/domain.hddl", "../../Examples/Minecraft-Player/p-013-013-013-013.hddl", strategy)
    # Minecraft Regular Problems
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-003-003-003-003.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-003-004-003-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-003-004-004-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-004-004-004-004.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-004-005-004-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-004-005-005-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-005-005-005-005.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-005-006-005-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-005-006-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-06.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-07.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-08.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-09.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-10.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-11.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-12.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-13.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-14.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-15.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-16.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-17.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-18.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-19.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-20.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-25.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-30.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-35.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-40.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-45.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-5-5-5-50.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-006-006-006-006.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-006-007-006-007.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-006-007-007-007.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-007-007-007-007.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-007-008-007-008.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-007-008-008-008.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-008-008-008-008.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-008-009-008-009.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-008-009-009-009.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-009-009-009-009.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-10.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-15.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-20.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-25.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-30.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-35.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-40.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-45.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-9-9-9-50.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-010-009-009-010.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-010-010-010-010.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-015-015-015-015.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-020-020-020-020.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-025-025-025-025.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-030-030-030-030.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-035-035-035-035.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-040-040-040-040.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-045-045-045-045.hddl", strategy)
    # run_test("../../Examples/Minecraft-Regular/domain.hddl", "../../Examples/Minecraft-Regular/p-050-050-050-050.hddl", strategy)
    # Monroe Fully Ob Problems
    run_test("../../Examples/Monroe-Fully-Observable/pfile01-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile01.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile02-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile02.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile03-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile03.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile04-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile04.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile05-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile05.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile06-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile06.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile07-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile07.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile08-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile08.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile09-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile09.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile10-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile10.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile11-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile11.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile12-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile12.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile13-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile13.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile14-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile14.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile15-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile15.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile16-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile16.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile17-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile17.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile18-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile18.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile19-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile19.hddl", strategy)
    run_test("../../Examples/Monroe-Fully-Observable/pfile20-domain.hddl", "../../Examples/Monroe-Fully-Observable/pfile20.hddl", strategy)
    # Monroe Partially Ob Problems
    run_test("../../Examples/Monroe-Partially-Observable/pfile01-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile01.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile02-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile02.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile03-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile03.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile04-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile04.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile05-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile05.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile06-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile06.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile07-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile07.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile08-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile08.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile09-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile09.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile10-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile10.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile11-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile11.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile12-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile12.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile13-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile13.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile14-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile14.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile15-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile15.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile16-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile16.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile17-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile17.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile18-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile18.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile19-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile19.hddl", strategy)
    run_test("../../Examples/Monroe-Partially-Observable/pfile20-domain.hddl", "../../Examples/Monroe-Partially-Observable/pfile20.hddl", strategy)
    # Multi-Arm Blocksworld Problems
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_01_005.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_01_010.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_005.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_010.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_015.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_020.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_025.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_030.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_035.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_040.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_045.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_050.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_055.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_060.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_065.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_070.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_075.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_080.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_085.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_090.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_095.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_02_100.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_03_025.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_03_030.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_005.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_010.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_015.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_020.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_025.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_030.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_035.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_040.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_045.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_050.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_055.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_060.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_065.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_070.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_075.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_085.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_090.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_095.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_04_100.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_05_045.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_05_050.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_005.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_010.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_015.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_020.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_025.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_030.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_035.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_040.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_045.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_050.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_055.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_060.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_065.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_070.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_075.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_080.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_085.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_090.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_095.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_06_100.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_07_065.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_07_070.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_08_075.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_08_080.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_09_085.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_09_090.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_10_095.hddl", strategy)
    run_test("../../Examples/Multiarm-Blocksworld/domain.hddl", "../../Examples/Multiarm-Blocksworld/pfile_10_100.hddl", strategy)
    # Robot Problems
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_01_001.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_02_001.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_02_002.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_03_001.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_03_002.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_03_003.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_03_005.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_04_003.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_04_005.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_05_005.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_05_010.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_10_020.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_15_030.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_20_040.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_25_050.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_30_060.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_35_070.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_40_080.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_45_090.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_50_100.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_60_120.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_70_140.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_80_160.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_90_180.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_100_200.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_110_220.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_120_240.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_130_260.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_140_280.hddl", strategy)
    run_test("../../Examples/Robot/domain.hddl", "../../Examples/Robot/pfile_150_300.hddl", strategy)
    # Snake Problems
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb01.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb02.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb03.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb04.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb05.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb06.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb07.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb08.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb09.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb10.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb11.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb12.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb13.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb14.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb15.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb16.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb17.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb18.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb19.snake.hddl", strategy)
    run_test("../../Examples/Snake/domain.hddl", "../../Examples/Snake/pb20.snake.hddl", strategy)
    # Towers Problems
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_01.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_02.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_03.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_04.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_05.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_06.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_07.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_08.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_09.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_10.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_11.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_12.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_13.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_14.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_15.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_16.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_17.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_18.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_19.hddl", strategy)
    run_test("../../Examples/Towers/domain.hddl", "../../Examples/Towers/pfile_20.hddl", strategy)
    # Transport
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile01.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile02.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile03.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile04.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile05.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile06.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile07.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile08.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile09.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile10.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile11.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile12.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile13.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile14.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile15.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile16.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile17.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile18.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile19.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile20.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile21.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile22.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile23.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile24.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile25.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile26.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile27.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile28.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile29.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile30.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile31.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile32.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile33.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile34.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile35.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile36.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile37.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile38.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile39.hddl", strategy)
    run_test("../../Examples/Transport/domain.hddl", "../../Examples/Transport/pfile40.hddl", strategy)
    # Woodworking Problems
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/01--p01-complete.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/02--p02-part1.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/03--p02-part2.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/04--p02-part3.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/05--p02-part4.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/06--p02-complete.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/07--p03-part1.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/08--p03-part2.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/09--p03-complete.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/10--p04-part1.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/11.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/12.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/13.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/14.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/15.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/16.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/17.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/18.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/19.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/20.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/21.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/22.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/23.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/24.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/25.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/26.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/27.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/28.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/29.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/30.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/31.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/32.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/33.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/34.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/35.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/36.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/37.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/38.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/39.hddl", strategy)
    run_test("../../Examples/Woodworking/domain.hddl", "../../Examples/Woodworking/40.hddl", strategy)
    """
