import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Solver.Models.default_model import DefaultModel
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Solver.Solving_Algorithms.total_order import TotalOrderSolver
from Parsers.HDDL_Parser import HDDLParser
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Internal_Representation.subtasks import Subtasks, Subtask
from Internal_Representation.state import State
from Internal_Representation.reg_parameter import RegParameter
from Solver.Progress_Tracking.action_tracker import ActionTracker
from Solver.Heuristics.no_pruning import NoPruning
from Solver.Heuristics.hamming_distance import HammingDistance
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection
import Tests.TestTools.rover_execution as RovEx
from Tests.TestTools.env_setup import env_setup
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker
from Solver.Solving_Algorithms.solver import Solver
from Solver.Models.model import Model


class SolvingTests(unittest.TestCase):

    def setUp(self) -> None:
        self.basic_domain_path = "Examples/Basic/basic.hddl"
        self.basic_pb1_path = "Examples/Basic/pb1.hddl"
        self.test_tools_path = "Tests/TestTools/"
        self.blocksworld_path = "Examples/Blocksworld/"
        self.rover_path = "Examples/IPC_Tests/Rover/"
        self.rover_col_path = "Examples/Rover/"
        self.IPC_Tests_path = "Examples/IPC_Tests/"
        self.barman_path = "Examples/Barman/"

    @unittest.skip
    def test_action_execution(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.blocksworld_path + "domain.hddl")
        parser.parse_problem(self.blocksworld_path + "pb1.hddl")

        solver = Solver(domain, problem)
        model = Model(solver.problem, solver, solver._available_modifiers)
        action = domain.get_action("pickup")    # b1

        solver._Solver__execute(model, action, {'?b': problem.get_object("b1")})

        # Check model.current_state.elements
        self.assertEqual([['clear', 'b3'],['on-table', 'b2'], ['on', 'b3', 'b5'],
        ['on', 'b5', 'b4'], ['on', 'b4', 'b2'],
        ['goal_clear', 'b2'], ['goal_on-table', 'b4'],['goal_on', 'b2', 'b5'],
        ['goal_on', 'b5', 'b4'], ['goal_clear', 'b1'],['goal_on-table', 'b3'],
        ['goal_on', 'b1', 'b3'], ['holding', 'b1']], model.current_state.elements)

        # Check model.current_state._index
        self.assertEqual({'clear': [0],'goal_clear': [5, 9],
        'goal_on': [7, 8, 11],'goal_on-table': [6, 10],'on': [2, 3, 4],
        'on-table': [1],'holding':[12]}, model.current_state._index)

    @unittest.skip
    def test_action_execution_2(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.blocksworld_path + "domain.hddl")
        parser.parse_problem(self.blocksworld_path + "pb1.hddl")

        solver = Solver(domain, problem)
        model = Model(solver.problem, solver, solver._available_modifiers)
        action = domain.get_action("mark_done") # b3
        solver._Solver__execute(model, action, {'?b': problem.get_object("b3")})

        # Check elements list
        expected_elements = ['hand-empty', ['clear', 'b3'],
                          ['on-table', 'b2'], ['on', 'b3', 'b5'], ['on', 'b5', 'b4'],['on', 'b4', 'b2'],
                          ['clear', 'b1'], ['on-table', 'b1'], ['goal_clear', 'b2'],['goal_on-table', 'b4'],
                          ['goal_on', 'b2', 'b5'], ['goal_on', 'b5', 'b4'], ['goal_clear', 'b1'],
                          ['goal_on-table', 'b3'], ['goal_on', 'b1', 'b3'], ['done', 'b3']]
        self.assertEqual(expected_elements, model.current_state.elements)

        expected_index = {'hand-empty': [0], 'clear': [1, 6], 'goal_clear': [8, 12],
                            'goal_on': [10, 11, 14], 'goal_on-table': [9, 13],
                            'on': [3, 4, 5], 'on-table': [2, 7], 'done': [15]}
        # Check _index dictionary
        self.assertEqual(expected_index, model.current_state._index)

    @unittest.skip
    def test_action_execution_3(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.blocksworld_path + "domain.hddl")
        parser.parse_problem(self.blocksworld_path + "pb1.hddl")

        solver = Solver(domain, problem)
        model = Model(solver.problem, solver, solver._available_modifiers)

        action = domain.get_action("pickup")  # b1
        solver._Solver__execute(model, action, {'?b': problem.get_object("b1")})

        action = domain.get_action("stack")
        solver._Solver__execute(model, action, {'?top': problem.get_object("b1"),
                                                '?bottom': problem.get_object("b3")})

        # Check elements list
        expected_elements = [['on-table', 'b2'], ['on', 'b3', 'b5'],
        ['on', 'b5', 'b4'], ['on', 'b4', 'b2'],
        ['goal_clear', 'b2'], ['goal_on-table', 'b4'],['goal_on', 'b2', 'b5'],
        ['goal_on', 'b5', 'b4'], ['goal_clear', 'b1'],['goal_on-table', 'b3'],
        ['goal_on', 'b1', 'b3'], 'hand-empty', ['on', 'b1', 'b3'], ['clear', 'b1']]
        self.assertEqual(expected_elements, model.current_state.elements)

        expected_index = {'goal_clear': [4, 8],
        'goal_on': [6, 7, 10],'goal_on-table': [5, 9],'on': [1, 2, 3, 12],
        'on-table': [0], 'hand-empty':[11], 'clear':[13]}
        # Check _index dictionary
        self.assertEqual(expected_index, model.current_state._index)

    @unittest.skip
    def test_action_execution_4(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.blocksworld_path + "domain.hddl")
        parser.parse_problem(self.blocksworld_path + "pb1.hddl")

        solver = Solver(domain, problem)
        model = Model(solver.problem, solver, solver._available_modifiers)
        action = domain.get_action("unstack")
        solver._Solver__execute(model, action, {'?top': problem.get_object("b3"),
                                                '?bottom' : problem.get_object("b5")})

        # Check elements list
        expected_elements = [['on-table', 'b2'], ['on', 'b5', 'b4'], ['on', 'b4', 'b2'],
                             ['clear', 'b1'], ['on-table', 'b1'], ['goal_clear', 'b2'],
                             ['goal_on-table', 'b4'],['goal_on', 'b2', 'b5'],
                             ['goal_on', 'b5', 'b4'], ['goal_clear', 'b1'],
                             ['goal_on-table', 'b3'], ['goal_on', 'b1', 'b3'],
                             ['holding', 'b3'], ['clear', 'b5']]
        self.assertEqual(expected_elements, model.current_state.elements)

        expected_index = {'clear': [3, 13], 'goal_clear': [5, 9],
                          'goal_on': [7, 8, 11], 'goal_on-table': [6, 10],
                          'on': [1, 2], 'on-table': [0, 4], 'holding': [12]}
        # Check _index dictionary
        self.assertEqual(expected_index, model.current_state._index)

    def test_action_execution_5(self):
        """Test Carrying out on action with one model and check the state of the others.
        Also check model state and _index"""

        domain, problem, parser, solver = env_setup(True, False)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")

        for i in range(7):
            solver.search_models._Q.put(DefaultModel(problem.initial_state.reproduce(),
                                                     [problem.subtasks.get_tasks()[1]], problem,
                                                     progress_tracker_class=SequentialTracker))
        for m in solver.search_models._Q.queue:
            m.ranking = 0

        # Execute action on model[7]
        subT = Subtask(domain.actions['visit'], [RegParameter('?from')])
        subT.add_given_parameters({'?waypoint': problem.objects['waypoint3']})
        solver._expand_action(subT, DefaultModel(problem.initial_state.reproduce(), [problem.subtasks.get_tasks()[1]], problem))

        search_models = solver.search_models._Q.queue
        self.assertEqual(8, len(search_models))
        for i in range(len(search_models) - 1):
            model = search_models[i]
            self.assertEqual(45, len(model.current_state.elements))
            self.assertEqual({'visible': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'at_soil_sample': [12, 14, 16],
             'at_rock_sample': [13, 15, 17], 'at_lander': [18], 'channel_free': [19], 'at': [20], 'available': [21],
             'store_of': [22], 'empty': [23], 'equipped_for_soil_analysis': [24], 'equipped_for_rock_analysis': [25],
             'equipped_for_imaging': [26], 'can_traverse': [27, 28, 29, 30, 31, 32], 'on_board': [33],
             'calibration_target': [34], 'supports': [35, 36], 'visible_from': [37, 38, 39, 40, 41, 42, 43, 44]},
                             model.current_state._index)
        model = search_models[7]
        self.assertEqual(46, len(model.current_state.elements))
        self.assertEqual({'visible': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 'at_soil_sample': [12, 14, 16],
                          'at_rock_sample': [13, 15, 17], 'at_lander': [18], 'channel_free': [19], 'at': [20],
                          'available': [21], 'store_of': [22], 'empty': [23], 'equipped_for_soil_analysis': [24],
                          'equipped_for_rock_analysis': [25],
                          'equipped_for_imaging': [26], 'can_traverse': [27, 28, 29, 30, 31, 32], 'on_board': [33],
                          'calibration_target': [34], 'supports': [35, 36],
                          'visible_from': [37, 38, 39, 40, 41, 42, 43, 44], 'visited': [45]},
                         model.current_state._index)

    def test_basic_execution_step_through(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)

        task = problem.subtasks.get_tasks()[0]
        self.assertEqual(domain.tasks['swap'], task.task)
        self.assertEqual([problem.objects['banjo'], problem.objects['kiwi']], task.parameters)

        # Initialise solver
        solver = PartialOrderSolver(domain, problem)

        # Create initial model
        solver.search_models.clear()
        param_dict = solver._generate_param_dict(task.task, task.parameters)
        task.add_given_parameters(param_dict)
        initial_model = DefaultModel(problem.initial_state, [task], problem, progress_tracker_class=SequentialTracker)
        solver.search_models.add(initial_model)

        # Execute Step 1
        solver._search(True)

        # Expect task to be expanded
        self.assertEqual(1, len(solver.search_models))
        self.assertEqual(1, len(solver.search_models._Q.queue[0].search_modifiers))

        self.assertEqual(domain.methods['have_second'], solver.search_models._Q.queue[0].search_modifiers[0].task)

        self.assertEqual(domain.predicates['have'],
                         solver.search_models._Q.queue[0].current_state.elements[0].predicate)
        self.assertEqual(1, len(solver.search_models._Q.queue[0].current_state.elements[0].objects))
        self.assertEqual(problem.objects['kiwi'], solver.search_models._Q.queue[0].current_state.elements[0].objects[0])
        self.assertEqual(None, solver.search_models._Q.queue[0].current_state.elements[0].objects[0].type)

        # Execute step 2
        solver._search(True)

        # Expect method to be expanded - should be tasks drop and pickup in the place of the method
        self.assertEqual(1, len(solver.search_models))
        self.assertEqual(2, len(solver.search_models._Q.queue[0].search_modifiers))

        model = solver.search_models._Q.queue[0]
        self.assertEqual(domain.actions['drop'], model.search_modifiers[0].task)
        self.assertEqual(domain.actions['pickup'], model.search_modifiers[1].task)

        self.assertEqual(domain.predicates['have'], model.current_state.elements[0].predicate)
        self.assertEqual(1, len(model.current_state.elements[0].objects))
        self.assertEqual(problem.objects['kiwi'], model.current_state.elements[0].
                         objects[0])
        self.assertEqual(None, model.current_state.elements[0].objects[0].type)

        # Execute step 3
        solver._search(True)

        # Expect the drop action to be carried out
        self.assertEqual(1, len(solver.search_models))
        model = solver.search_models._Q.queue[0]
        self.assertEqual(1, len(model.search_modifiers))
        self.assertEqual(domain.actions['pickup'], model.search_modifiers[0].task)
        self.assertEqual([], model.current_state.elements)

        # Execute step 4
        solver._search(True)

        # Expect the pickup action to be carried out
        self.assertEqual(0, len(solver.search_models))
        self.assertEqual(1, len(solver.search_models._completed_models))
        model = solver.search_models._completed_models[0]
        self.assertEqual(0, len(model.search_modifiers))

        # Check final state
        self.assertEqual(1, len(model.current_state.elements))
        self.assertEqual(domain.predicates['have'], model.current_state.elements[0].predicate)
        self.assertEqual(1, len(model.current_state.elements[0].objects))
        self.assertEqual(problem.objects['banjo'], model.current_state.elements[0].objects[0])

    def test_basic_execution_po(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)
        res = solver.solve()
        self.assertNotEqual(None, res)
        self.assertEqual(ActionTracker(domain.tasks['swap'], {'?x': problem.objects['banjo'],
                                                              '?y': problem.objects['kiwi']}), res.get_progress_tracker().operations_taken[0])
        self.assertEqual(ActionTracker(domain.methods['have_second'], {'?x': problem.objects['banjo'],
                                                                        '?y': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[1])
        self.assertEqual(ActionTracker(domain.actions['drop'], {'?a': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[2])
        self.assertEqual(ActionTracker(domain.actions['pickup'], {'?a': problem.objects['banjo']}),
                         res.get_progress_tracker().operations_taken[3])

    def test_basic_execution_to(self):
        domain, problem, parser, solver = env_setup(True, False)
        parser.parse_domain(self.basic_domain_path)
        parser.parse_problem(self.basic_pb1_path)
        res = solver.solve()
        self.assertNotEqual(None, res)
        self.assertEqual(ActionTracker(domain.tasks['swap'], {'?x': problem.objects['banjo'],
                                                              '?y': problem.objects['kiwi']}), res.get_progress_tracker().operations_taken[0])
        self.assertEqual(ActionTracker(domain.methods['have_second'], {'?x': problem.objects['banjo'],
                                                                        '?y': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[1])
        self.assertEqual(ActionTracker(domain.actions['drop'], {'?a': problem.objects['kiwi']}),
                         res.get_progress_tracker().operations_taken[2])
        self.assertEqual(ActionTracker(domain.actions['pickup'], {'?a': problem.objects['banjo']}),
                         res.get_progress_tracker().operations_taken[3])

    def test_compare_parameters(self):
        domain, problem, parser, solver = env_setup(True, False, parameter_selector=1)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")
        solver.solve(search=False)

        model = solver.search_models._Q.queue[0]
        response = solver.parameter_selector.compare_parameters(domain.methods['m_get_image_data_ordering_0'],
                                                                model.search_modifiers[0].given_params)
        self.assertEqual(list, type(response))
        self.assertEqual(2, len(response))
        self.assertEqual(bool, type(response[0]))
        self.assertEqual(list, type(response[1]))
        self.assertEqual(False, response[0])
        self.assertEqual(["?camera", "?rover", "?waypoint"], response[1])

    def test_finding_parameters(self):
        domain, problem, parser, solver = env_setup(True, False, parameter_selector=1)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")
        solver.solve(search=False)

        solver.parameter_selector.presolving_processing(domain, problem)
        model = solver.search_models.pop()
        method = domain.methods['m_get_image_data_ordering_0']
        found_params = solver.parameter_selector._find_satisfying_parameters(model,
                                                    method.requirements, model.search_modifiers[0].given_params)
        self.assertEqual(4, len(found_params))
        for combo in found_params:
            self.assertEqual(problem.objects['objective1'], combo['?objective'])
            self.assertEqual(problem.objects['high_res'], combo['?mode'])
            self.assertEqual(problem.objects['camera0'], combo['?camera'])
            self.assertEqual(problem.objects['rover0'], combo['?rover'])
        self.assertEqual(problem.objects['waypoint0'], found_params[0]['?waypoint'])
        self.assertEqual(problem.objects['waypoint1'], found_params[1]['?waypoint'])
        self.assertEqual(problem.objects['waypoint2'], found_params[2]['?waypoint'])
        self.assertEqual(problem.objects['waypoint3'], found_params[3]['?waypoint'])

    def test_rover_execution_beginning(self):
        domain, problem, parser, solver = env_setup(True, False)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")
        solver.solve(search=False)

        self.assertEqual(1, len(solver.search_models))
        model = solver.search_models._Q.queue[0]
        self.assertEqual(3, len(model.search_modifiers) + len(model.waiting_subtasks))
        self.assertEqual(Subtask, type(model.search_modifiers[0]))
        self.assertEqual(domain.tasks['get_image_data'], model.search_modifiers[0].task)
        self.assertEqual(2, len(model.search_modifiers[0].given_params))
        self.assertEqual(problem.objects['objective1'], model.search_modifiers[0].given_params['?objective'])
        self.assertEqual(problem.objects['high_res'], model.search_modifiers[0].given_params['?mode'])

    def test_rover_execution_1(self):
        domain, problem, parser, solver = env_setup(True, False)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")
        solver.solve(search=False)

        solver.parameter_selector.presolving_processing(domain, problem)
        solver._search(True)
        # Check searchModels has 4 search nodes each with a different ?waypoint parameter
        self.assertEqual(4, len(solver.search_models))
        for i in range(4):
            model = solver.search_models._Q.queue[i]
            self.assertEqual(3, len(model.search_modifiers) + len(model.waiting_subtasks))
            self.assertEqual(Subtask, type(model.search_modifiers[0]))
            self.assertEqual(domain.methods['m_get_image_data_ordering_0'], model.search_modifiers[0].task)
            self.assertEqual(problem.objects["waypoint" + str(i)], model.search_modifiers[0].given_params['?waypoint'])

    def test_rover_execution_complete_po(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_path + "rover-domain.hddl")
        parser.parse_problem(self.rover_path + "pfile01.hddl")
        solver.set_heuristic(NoPruning)
        res = solver.solve()
        image_data = domain.actions['communicate_image_data']
        soil_data = domain.actions['communicate_soil_data']
        rock_data = domain.actions['communicate_rock_data']
        necessary_actions = [image_data, soil_data, rock_data]
        for a in necessary_actions:
            # print("Testing {}".format(a))
            found = False
            for ac in res.get_progress_tracker().actions_taken:
                if a == ac.mod:
                    found = True
                    break
            self.assertEqual(True, found)

    def test_rover_execution_complete_to(self):
        domain, problem, parser, solver = env_setup(True, False)
        parser.parse_domain(self.rover_path + "rover-domain.hddl")
        parser.parse_problem(self.rover_path + "pfile01.hddl")
        solver.set_heuristic(NoPruning)
        res = solver.solve()
        image_data = domain.actions['communicate_image_data']
        soil_data = domain.actions['communicate_soil_data']
        rock_data = domain.actions['communicate_rock_data']
        necessary_actions = [image_data, soil_data, rock_data]
        for a in necessary_actions:
            # print("Testing {}".format(a))
            found = False
            for ac in res.get_progress_tracker().actions_taken:
                if a == ac.mod:
                    found = True
                    break
            self.assertEqual(True, found)

    def test_goal_state_satisfaction_po(self):
        # Some of the rover domains have goal states defined. Check that the returned plan satisfies the goal conditions
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.rover_col_path + "domain.hddl")
        parser.parse_problem(self.rover_col_path + "p01.hddl")
        solver = PartialOrderSolver(domain, problem)
        plan = solver.solve()
        self.assertEqual(True, problem.evaluate_goal(plan))

        rock_comm_pred = domain.predicates['communicated_rock_data']
        pred_obs = [problem.objects['waypoint0']]
        plan.current_state.remove_element(rock_comm_pred, pred_obs)
        self.assertEqual(False, problem.evaluate_goal(plan))

    def test_goal_state_satisfaction_to(self):
        # Some of the rover domains have goal states defined. Check that the returned plan satisfies the goal conditions
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.rover_col_path + "domain.hddl")
        parser.parse_problem(self.rover_col_path + "p01.hddl")
        solver = TotalOrderSolver(domain, problem)
        plan = solver.solve()
        self.assertEqual(True, problem.evaluate_goal(plan))

        rock_comm_pred = domain.predicates['communicated_rock_data']
        pred_obs = [problem.objects['waypoint0']]
        plan.current_state.remove_element(rock_comm_pred, pred_obs)
        self.assertEqual(False, problem.evaluate_goal(plan))

    def test_parameter_expansion(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "transport01/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "transport01/pfile01.hddl")

        task = problem.subtasks.get_tasks()[0]

        # Initialise solver
        solver.parameter_selector.presolving_processing(domain, problem)

        # Create initial model
        solver.search_models.clear()
        param_dict = solver._generate_param_dict(task.task, task.parameters)
        task.add_given_parameters(param_dict)
        initial_model = DefaultModel(problem.initial_state, [task], problem, progress_tracker_class=SequentialTracker)
        solver.search_models.add(initial_model)

        # Expand
        solver._search(True)
        search_models = solver.search_models._Q.queue

        model = search_models[0]
        self.assertEqual(4, len(model.search_modifiers[0].given_params))

    def test_distance_to_goal_heuristic(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_col_path + "domain.hddl")
        parser.parse_problem(self.rover_col_path + "p01.hddl")
        solver.set_heuristic(HammingDistance)
        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_total_order_rover(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")

        # Initialise solver
        solver = TotalOrderSolver(domain, problem)
        solver.set_heuristic(NoPruning)

        res = solver.solve()
        image_data = domain.actions['communicate_image_data']
        soil_data = domain.actions['communicate_soil_data']
        rock_data = domain.actions['communicate_rock_data']
        necessary_actions = [image_data, soil_data, rock_data]
        for a in necessary_actions:
            # print("Testing {}".format(a))
            found = False
            for ac in res.get_progress_tracker().actions_taken:
                if a == ac.mod:
                    found = True
                    break
            self.assertEqual(True, found)

    def test_total_order_basic(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain("Examples/IPC_Tests/Rover/rover-domain.hddl")
        parser.parse_problem("Examples/IPC_Tests/Rover/pfile01.hddl")

        # Initialise solver
        solver = TotalOrderSolver(domain, problem)
        solver.set_heuristic(NoPruning)

        res = solver.solve()
        self.assertNotEqual(None, res)

    def test_barman_1(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.barman_path + "domain.hddl")
        parser.parse_problem(self.barman_path + "pfile01.hddl")

        res = solver.solve()
        self.assertIsNotNone(res)
