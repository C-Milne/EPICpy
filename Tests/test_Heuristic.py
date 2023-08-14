import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from queue import PriorityQueue
from Tests.TestTools.env_setup import env_setup
from Solver.Heuristics.tree_distance import TreeDistance
from Solver.Heuristics.hamming_distance_seen_states import HammingDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance_seen_states import TreeDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance_partial_order import TreeDistancePartialOrder
from Solver.Heuristics.delete_relaxed import DeleteRelaxed, AltPrecondition, AltOperatorCondition
from Solver.Heuristics.hamming_distance import HammingDistance
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Heuristics.landmarks import Landmarks
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Internal_Representation.conditions import PredicateCondition
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.subtasks import Subtask
from Solver.Models.default_model import DefaultModel
from Solver.Models.PandaVerifyModel import PandaVerifyModel
from Solver.Models.model import Model
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from Internal_Representation.state import State


class HeuristicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport_path = "Examples/IPC_Tests/transport01/"
        self.rover_path = "Examples/Rover/"
        self.basic_path = "Examples/Basic/"
        self.depot_path = "Examples/Depots/"
        self.rover_PO_path = "Examples/Partial_Order/Rover/"
        Model.model_counter = 0

    def test_tree_distance_preprocessing(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.transport_path + "domain.hddl")
        parser.parse_problem(self.transport_path + "pfile01.hddl")
        solver.set_heuristic(TreeDistance)
        solver.search_models.heuristic.presolving_processing()
        heu = solver.search_models.heuristic
        self.assertEqual(14, len(heu.tree.nodes))

        node = heu.tree.nodes['deliver']
        self.assertEqual(14, node.distance)

        node = heu.tree.nodes['get_to']
        self.assertEqual(3, node.distance)

        node = heu.tree.nodes['unload']
        self.assertEqual(3, node.distance)

        node = heu.tree.nodes['load']
        self.assertEqual(3, node.distance)

        node = heu.tree.nodes['m_unload_ordering_0']
        self.assertEqual(2, node.distance)

        node = heu.tree.nodes['m_load_ordering_0']
        self.assertEqual(2, node.distance)

        node = heu.tree.nodes['m_i_am_there_ordering_0']
        self.assertEqual(2, node.distance)

        node = heu.tree.nodes['m_drive_to_via_ordering_0']
        self.assertEqual(5, node.distance)

        node = heu.tree.nodes['m_drive_to_ordering_0']
        self.assertEqual(2, node.distance)

    def test_tree_distance_execution(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p03.hddl")
        solver.set_heuristic(TreeDistance)
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_partial_order_tree_distance_execution(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_PO_path + "domain.hddl")
        parser.parse_problem(self.rover_PO_path + "pfile01.hddl")
        solver.set_heuristic(TreeDistancePartialOrder)
        res = solver.solve()
        self.assertNotEqual(None, res)

    @unittest.skip
    def test_delete_relaxed_preprocessing_basic_alt_domain(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(DeleteRelaxed)
        solver.search_models.heuristic.presolving_processing()
        heu = solver.search_models.heuristic
        alt_domain = heu.alt_domain

        # Check actions
        self.assertIn("pickup-banjo", alt_domain.actions)
        self.assertIn("pickup-kiwi", alt_domain.actions)
        self.assertIn("drop-banjo", alt_domain.actions)
        self.assertIn("drop-kiwi", alt_domain.actions)
        self.assertEqual(4, len(alt_domain.actions))

        self.assertEqual(domain.actions['pickup'].preconditions, alt_domain.actions['pickup-banjo'].preconditions)
        self.assertEqual(domain.actions['pickup'].preconditions, alt_domain.actions['pickup-kiwi'].preconditions)

        self.assertEqual(domain.actions['pickup'].parameters, alt_domain.actions['pickup-banjo'].parameters)
        self.assertEqual(domain.actions['pickup'].parameters, alt_domain.actions['pickup-kiwi'].parameters)

        self.assertEqual(AltPrecondition, type(alt_domain.actions['pickup-kiwi'].preconditions))
        self.assertEqual(AltOperatorCondition, type(alt_domain.actions['pickup-kiwi'].preconditions.head))

        self.assertEqual(domain.actions['drop'].preconditions, alt_domain.actions['drop-banjo'].preconditions)
        self.assertEqual(domain.actions['drop'].preconditions, alt_domain.actions['drop-kiwi'].preconditions)

        self.assertEqual(domain.actions['drop'].parameters, alt_domain.actions['drop-banjo'].parameters)
        self.assertEqual(domain.actions['drop'].parameters, alt_domain.actions['drop-kiwi'].parameters)

        # Check methods
        self.assertIn("have_first-banjo-banjo", alt_domain.methods)
        self.assertIn("have_first-banjo-kiwi", alt_domain.methods)
        self.assertIn("have_first-kiwi-banjo", alt_domain.methods)
        self.assertIn("have_first-kiwi-kiwi", alt_domain.methods)
        self.assertIn("have_second-banjo-banjo", alt_domain.methods)
        self.assertIn("have_second-banjo-kiwi", alt_domain.methods)
        self.assertIn("have_second-kiwi-banjo", alt_domain.methods)
        self.assertIn("have_second-kiwi-kiwi", alt_domain.methods)
        self.assertEqual(8, len(alt_domain.methods))

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-banjo']),
                      alt_domain.methods["have_first-banjo-banjo"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-banjo']),
                      alt_domain.methods["have_first-banjo-banjo"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-banjo']),
                      alt_domain.methods["have_first-banjo-kiwi"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-kiwi']),
                      alt_domain.methods["have_first-banjo-kiwi"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-kiwi']),
                      alt_domain.methods["have_first-kiwi-banjo"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-banjo']),
                      alt_domain.methods["have_first-kiwi-banjo"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-kiwi']),
                      alt_domain.methods["have_first-kiwi-kiwi"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-kiwi']),
                      alt_domain.methods["have_first-kiwi-kiwi"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-banjo']),
                      alt_domain.methods["have_second-banjo-banjo"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-banjo']),
                      alt_domain.methods["have_second-banjo-banjo"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-kiwi']),
                      alt_domain.methods["have_second-banjo-kiwi"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-banjo']),
                      alt_domain.methods["have_second-banjo-kiwi"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-banjo']),
                      alt_domain.methods["have_second-kiwi-banjo"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-kiwi']),
                      alt_domain.methods["have_second-kiwi-banjo"].preconditions.head.children)

        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['drop-kiwi']),
                      alt_domain.methods["have_second-kiwi-kiwi"].preconditions.head.children)
        self.assertIn(PredicateCondition(alt_domain.predicates["U"], ['pickup-kiwi']),
                      alt_domain.methods["have_second-kiwi-kiwi"].preconditions.head.children)

        self.assertEqual(AltPrecondition, type(alt_domain.methods["have_first-banjo-kiwi"].preconditions))
        self.assertEqual(AltOperatorCondition, type(alt_domain.methods["have_first-banjo-kiwi"].preconditions.head))
        self.assertIsInstance(alt_domain.methods["have_first-banjo-kiwi"].preconditions.head.children[0], PredicateCondition)
        self.assertEqual(AltOperatorCondition, type(alt_domain.methods["have_first-banjo-kiwi"].preconditions.head.children[1]))

    @unittest.skip
    def test_delete_relaxed_preprocessing_basic_alt_problem(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(DeleteRelaxed)
        solver.search_models.heuristic.presolving_processing()
        heu = solver.search_models.heuristic
        alt_problem = heu.alt_problem
        self.assertEqual(problem.initial_state, alt_problem.initial_state)

        # Check objects
        self.assertIn("kiwi", alt_problem.objects)
        self.assertIn("banjo", alt_problem.objects)

        # Check objects for modifiers
        self.assertIn("drop-kiwi", alt_problem.objects)
        self.assertIn("drop-banjo", alt_problem.objects)
        self.assertIn("pickup-kiwi", alt_problem.objects)
        self.assertIn("pickup-banjo", alt_problem.objects)
        self.assertIn("have_first-banjo-kiwi", alt_problem.objects)
        self.assertIn("have_first-banjo-banjo", alt_problem.objects)
        self.assertIn("have_first-kiwi-banjo", alt_problem.objects)
        self.assertIn("have_first-kiwi-kiwi", alt_problem.objects)
        self.assertIn("have_second-banjo-kiwi", alt_problem.objects)
        self.assertIn("have_second-banjo-banjo", alt_problem.objects)
        self.assertIn("have_second-kiwi-banjo", alt_problem.objects)
        self.assertIn("have_second-kiwi-kiwi", alt_problem.objects)
        self.assertIn("swap-banjo-kiwi", alt_problem.objects)
        self.assertIn("swap-banjo-banjo", alt_problem.objects)
        self.assertIn("swap-kiwi-banjo", alt_problem.objects)
        self.assertIn("swap-kiwi-kiwi", alt_problem.objects)

    def test_delete_relaxed_basic_execution_setup(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(DeleteRelaxed)
        solver.solve(search=False)
        search_models = solver.search_models
        self.assertEqual(1, len(search_models))
        self.assertEqual(2, search_models._Q.queue[0].ranking)

    def test_delete_relaxed_choose_targets(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(DeleteRelaxed)
        heu = solver.search_models.heuristic
        heu.presolving_processing()

        subtasks_orderings = problem.subtasks.get_task_orderings()
        subtasks = subtasks_orderings[0]
        list_subT = []
        num_tasks = len(subtasks)
        task_counter = 0
        while task_counter < num_tasks:
            subT = subtasks[task_counter]
            if subT == "and" or subT == "or":
                del subtasks[task_counter]
                num_tasks -= 1
                continue

            # Create initial search model
            param_dict = solver._generate_param_dict(subT.task, subT.parameters)
            subT.add_given_parameters(param_dict)
            list_subT.append(subT)
            task_counter += 1

        model = DefaultModel(problem.initial_state.reproduce(), list_subT, problem, [])
        targets = heu._get_target_tasks(model)
        self.assertNotEqual([], targets)
        self.assertEqual(['U-swap--banjo--kiwi'], targets)

    @unittest.skip
    def test_delete_relaxed_basic(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(DeleteRelaxed)
        res = solver.solve()
        self.assertNotEqual(None, res)

    @unittest.skip
    def test_delete_relaxed_rover_1(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(DeleteRelaxed)
        res = solver.solve()
        self.assertNotEqual(None, res)

    @unittest.skip
    def test_delete_relaxed_depot_1(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.depot_path + "domain.hddl")
        parser.parse_problem(self.depot_path + "p01.hddl")
        solver.set_heuristic(DeleteRelaxed)
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_Hamming_Distance_basic(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(HammingDistance)
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_Hamming_Distance_rover(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(HammingDistance)
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_seen_states_pruning_rover(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(SeenStatesPruning)
        res = solver.solve()
        self.assertIsNotNone(res)
        self.assertEqual(271, res.model_counter)

    def test_seen_states_pruning(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(SeenStatesPruning)

        models = []
        for i in range(2):
            # Create a model
            state1 = State()
            state1.add_element(ProblemPredicate(domain.get_predicate('at'), [problem.get_object('rover0'), problem.get_object('waypoint0')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint0')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint1')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint2')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'), [problem.get_object('objective0'), problem.get_object('waypoint3')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'), [problem.get_object('rover0'), problem.get_object('waypoint0'), problem.get_object('waypoint1')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'), [problem.get_object('rover0'), problem.get_object('waypoint0'), problem.get_object('waypoint3')]))
            state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'), [problem.get_object('rover0'), problem.get_object('waypoint2'), problem.get_object('waypoint3')]))

            search_modifiers1 = []
            task = domain.get_task('do_calibrate')
            subt = Subtask(task, task.get_parameters())
            subt_given_params = {}
            for p in zip(task.get_parameters(), [problem.get_object('rover0'), problem.get_object('camera0')]):
                subt_given_params[p[0].name] = p[1]
            subt.add_given_parameters(subt_given_params)
            search_modifiers1.append(subt)

            task = domain.get_method('m2_do_navigate2')
            subt = Subtask(task, task.get_parameters())
            subt_given_params = {}
            for p in zip(task.get_parameters(), [problem.get_object('rover0'), problem.get_object('waypoint0'), problem.get_object('waypoint1')]):
                subt_given_params[p[0].name] = p[1]
            subt.add_given_parameters(subt_given_params)
            search_modifiers1.append(subt)

            task = domain.get_action('take_image')
            subt = Subtask(task, task.get_parameters())
            subt_given_params = {}
            for p in zip(task.get_parameters(),
                         [problem.get_object('rover0'),
                          problem.get_object('waypoint2'),
                          problem.get_object('objective1'), problem.get_object('camera0'), problem.get_object('high_res')]):
                subt_given_params[p[0].name] = p[1]
            subt.add_given_parameters(subt_given_params)
            search_modifiers1.append(subt)

            waiting_subtasks1 = []
            task = domain.get_task('get_soil_data')
            subt = Subtask(task, task.get_parameters())
            subt_given_params = {}
            for p in zip(task.get_parameters(),
                         [problem.get_object('waypoint2')]):
                subt_given_params[p[0].name] = p[1]
            subt.add_given_parameters(subt_given_params)
            waiting_subtasks1.append(subt)

            task = domain.get_task('get_rock_data')
            subt = Subtask(task, task.get_parameters())
            subt_given_params = {}
            for p in zip(task.get_parameters(),
                         [problem.get_object('waypoint1')]):
                subt_given_params[p[0].name] = p[1]
            subt.add_given_parameters(subt_given_params)
            waiting_subtasks1.append(subt)
            models.append(DefaultModel(state1, search_modifiers1, problem, waiting_subtasks1, progress_tracker_class=SequentialTracker))

        # Add model to search queue
        model1, model2 = models
        solver.search_models.heuristic.ranking(model1)
        solver.search_models.heuristic.ranking(model2)
        seen_states = list(solver.search_models.heuristic._seen_states)
        self.assertEqual(1, len(seen_states))

    def test_seen_states_pruning_panda_verify(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(SeenStatesPruning)

        state1 = State()
        state1.add_element(ProblemPredicate(domain.get_predicate('at'),
                                            [problem.get_object('rover0'), problem.get_object('waypoint0')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'),
                                            [problem.get_object('objective0'), problem.get_object('waypoint0')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'),
                                            [problem.get_object('objective0'), problem.get_object('waypoint1')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'),
                                            [problem.get_object('objective0'), problem.get_object('waypoint2')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('visible_from'),
                                            [problem.get_object('objective0'), problem.get_object('waypoint3')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'),
                                            [problem.get_object('rover0'), problem.get_object('waypoint0'),
                                             problem.get_object('waypoint1')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'),
                                            [problem.get_object('rover0'), problem.get_object('waypoint0'),
                                             problem.get_object('waypoint3')]))
        state1.add_element(ProblemPredicate(domain.get_predicate('can_traverse'),
                                            [problem.get_object('rover0'), problem.get_object('waypoint2'),
                                             problem.get_object('waypoint3')]))

        search_modifiers1 = []
        search_modifiers2 = []
        waiting_subtasks1 = []
        task = domain.get_task('do_calibrate')
        subt = Subtask(task, task.get_parameters())
        subt_given_params = {'?x': problem.get_object('rover0'), '?c': problem.get_object('camera0')}
        subt.add_given_parameters(subt_given_params)
        search_modifiers1.append(subt)
        search_modifiers2.append(subt)

        task = domain.get_task('get_rock_data')
        subt = Subtask(task, task.get_parameters())
        subt_given_params = {'?from': problem.get_object('waypoint1')}
        subt.add_given_parameters(subt_given_params)
        search_modifiers1.append(subt)
        search_modifiers2.append(subt)

        subt = Subtask(task, task.get_parameters())
        subt_given_params = {'?from': problem.get_object('waypoint2')}
        subt.add_given_parameters(subt_given_params)
        waiting_subtasks1.append(subt)

        model1 = PandaVerifyModel(state1, search_modifiers1, problem, waiting_subtasks1, progress_tracker_class=PandaVerifyFormatTracker)
        model2 = PandaVerifyModel(state1, search_modifiers2, problem, waiting_subtasks1, progress_tracker_class=PandaVerifyFormatTracker)
        solver.search_models.heuristic.ranking(model1)
        solver.search_models.heuristic.ranking(model2)
        seen_states = list(solver.search_models.heuristic._seen_states)
        self.assertEqual(1, len(seen_states))

    def test_seen_states_hamming_distance(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(HammingDistanceSeenStatesPruning)
        solver.set_search_queue(GBFSSearchQueue)
        res = solver.solve()
        self.assertIsNotNone(res)

    def test_seen_states_tree_distance(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(TreeDistanceSeenStatesPruning)
        solver.set_search_queue(GBFSSearchQueue)
        res = solver.solve()
        self.assertIsNotNone(res)

    def test_landmarks_basic(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_path + "basic.hddl")
        parser.parse_problem(self.basic_path + "pb1.hddl")
        solver.set_heuristic(Landmarks)
        solver.set_search_queue(GBFSSearchQueue)
        res = solver.solve()
        self.assertIsNotNone(res)

    def test_landmarks_rover_1(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "domain.hddl")
        parser.parse_problem(self.rover_path + "p01.hddl")
        solver.set_heuristic(Landmarks)
        solver.set_search_queue(GBFSSearchQueue)
        res = solver.solve()
        self.assertIsNotNone(res)
