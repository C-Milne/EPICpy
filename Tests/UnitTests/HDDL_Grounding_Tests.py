import unittest
from Solver.model import Model
from Parsers.HDDL_Parser import HDDLParser
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Internal_Representation.modifier import Modifier
from Solver.Solving_Algorithms.solver import Solver
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Internal_Representation.predicate import Predicate
from Internal_Representation.state import State
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.Object import Object
from Tests.UnitTests.TestTools.env_setup import env_setup
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection


class HDDLGroundingTests(unittest.TestCase):

    def setUp(self) -> None:
        self.basic_domain_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"
        self.basic_pb1_path_SHOP = "../Examples/Basic/pb1.shop"
        self.test_tools_path = "TestTools/"
        self.blocksworld_path = "../Examples/Blocksworld/"
        self.rover_path = "../Examples/IPC_Tests/Rover/"
        self.rover_col_path = "../Examples/Rover/"
        self.IPC_Tests_path = "../Examples/IPC_Tests/"

    def test_precondition_complex(self):
        domain, problem, parser, solver = env_setup(True)
        # Devise a complex precondition and test it
        precon_list = ['and',
                       ['not',
                        ['and', ['have', '?y'], ['have', '?a']]
                        ],
                       ['and',
                        ['have', '?x'], ['or', ['have', '?b'], ['have', '?c']]
                        ],
                       ['or',
                        ['hate', '?z'], ['hate', '?d']
                        ]
                       ]
        # Set up values
        have_pred = Predicate('have', [RegParameter('?x')])
        hate_pred = Predicate('hate', [RegParameter('?a')])
        domain.add_predicate(have_pred)
        domain.add_predicate(hate_pred)

        precons = parser._parse_precondition(precon_list)


        ob_ham = Object("ham")
        ob_irnbru = Object('irn-bru')
        ob_car = Object('car')
        ob_bike = Object('bike')
        ob_popcorn = Object('popcorn')
        ob_crisps = Object('crisps')
        ob_dark = Object('dark')

        # Set up model - {'have': ['ham', 'irn-bru', 'car'], 'hate': []}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_ham]))
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))

        model = Model(state, [])
        param_dict = {"?z": ob_ham, "?x": ob_irnbru, "?y": ob_car, "?a": ob_bike, "?b": ob_popcorn,
                      "?c": ob_crisps, "?d": ob_dark}

        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(False, result)

        # Set up next model - {'have': ['ham', 'irn-bru', 'car', 'popcorn'], 'hate': ['dark']}
        state.add_element(ProblemPredicate(have_pred, [ob_popcorn]))
        state.add_element(ProblemPredicate(hate_pred, [ob_dark]))
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

    def test_method_requirements(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.test_tools_path + "Blocksworld/Blocksworld_test_domain_2.hddl")
        solver = PartialOrderSolver(domain, problem)
        solver.parameter_selector.presolving_processing(domain, problem)

        # Add some assertions for this - seems too work (perhaps not for 'forall' methods)
        self.assertEqual(2, len(domain.methods['pickup-ready-block'].requirements))
        self.assertEqual({'type': domain.types['block'], 'predicates': {'and': {'clear': 1, 'not': {'done': 1}, 'goal_on': 1}}},
                         domain.methods['pickup-ready-block'].requirements['?b'])
        self.assertEqual({'type': domain.types['block'],
                          'predicates': {'and': {'goal_on': 2, 'done': 1, 'clear': 1}}},
                         domain.methods['pickup-ready-block'].requirements['?d'])

    def test_forall_preconditions(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        # Test preconditions
        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.test_tools_path + "Blocksworld/Blocksworld_test_domain_1.hddl")
        parser.parse_problem(self.test_tools_path + "Blocksworld/Blocksworld_test_problem_1.hddl")
        method = domain.methods['setdone']
        model = Model(problem.initial_state, [], problem)
        result = method.evaluate_preconditions(model, {}, problem)
        self.assertEqual(False, result)

        # Test for True
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        # Test preconditions
        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.test_tools_path + "Blocksworld/Blocksworld_test_domain_1.hddl")
        parser.parse_problem(self.test_tools_path + "Blocksworld/Blocksworld_test_problem_1_1.hddl")
        method = domain.methods['setdone']
        model = Model(problem.initial_state, [], problem)
        result = method.evaluate_preconditions(model, {}, problem)
        self.assertEqual(True, result)

    def test_forall_preconditions_2(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "test02_forall/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "test02_forall/problem.hddl")
        plan = solver.solve()
        solver.output(plan)
        self.assertIsNotNone(plan)
        self.assertEqual(1, len(plan.get_progress_tracker().actions_taken))

        problem.initial_state.remove_element(domain.predicates['foo'], [problem.objects['a']])
        solver = PartialOrderSolver(domain, problem)
        plan = solver.solve()
        solver.output(plan)
        self.assertIsNone(plan)

    def test_precondition_and(self):
        domain, problem, parser, solver = env_setup(True)
        # Test the 'and' functionality for preconditions
        # Set up values
        have_pred = Predicate('have', [RegParameter('?x')])
        domain.add_predicate(have_pred)

        ob_ham = Object("ham")
        ob_irnbru = Object('irn-bru')
        ob_car = Object('car')

        # Set up precondition object
        precon_list = ['and', ['have', '?x'], ['have', '?y'], ['have', '?z']]
        precons = parser._parse_precondition(precon_list)

        # Set up model - {'have': ['ham', 'irn-bru', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_ham]))
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        param_dict = {"?z": ob_ham, "?x": ob_irnbru, "?y": ob_car}

        # Testing for True
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

        # Testing for False - {'have': ['irn-bru', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(False, result)

    def test_precondition_or(self):
        domain, problem, parser, solver = env_setup(True)
        domain.add_predicate(Predicate('have'))
        # Test the 'or' functionality for preconditions
        # Set up precondition object
        precon_list = ['or', ['have', '?x'], ['have', '?y'], ['have', '?z']]
        precons = parser._parse_precondition(precon_list)

        # Set up values
        have_pred = Predicate('have', [RegParameter('?x')])
        ob_ham = Object("ham")
        ob_irnbru = Object('irn-bru')
        ob_car = Object('car')

        # Set up model - {'have': ['ham', 'irn-bru', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_ham]))
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        param_dict = {"?z": ob_ham, "?x": ob_irnbru, "?y": ob_car}

        # Testing for True
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

        # Testing for True - {'have': ['irn-bru', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

        # {'have': ['irn-bru']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

        # {'have': []}
        state = State()
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(False, result)

    def test_precondition_not(self):
        domain, problem, parser, solver = env_setup(True)
        domain.add_predicate(Predicate('have'))
        # Test the 'not' functionality for preconditions
        # Set up precondition object
        precon_list = ['not', ['have', '?x']]
        precons = parser._parse_precondition(precon_list)

        # Set up values
        have_pred = Predicate('have', [RegParameter('?x')])
        ob_ham = Object("ham")
        ob_irnbru = Object('irn-bru')
        ob_car = Object('car')

        # Set up model - {'have': ['ham', 'irn-bru', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_ham]))
        state.add_element(ProblemPredicate(have_pred, [ob_irnbru]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        param_dict = {"?z": ob_ham, "?x": ob_irnbru, "?y": ob_car}

        # Testing for False
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(False, result)

        # Testing for True - {'have': ['ham', 'car']}
        state = State()
        state.add_element(ProblemPredicate(have_pred, [ob_ham]))
        state.add_element(ProblemPredicate(have_pred, [ob_car]))
        model = Model(state, [])
        result = precons.evaluate(param_dict, model, None)
        self.assertEqual(True, result)

    @unittest.skip
    def test_upgraded_precondition(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.rover_col_path + "domain.hddl")
        method = domain.methods['m9_send_soil_data']
        # ['and', ['at_lander', '?l', '?w1'], ['visible', '?from', '?w1'], ['at', '?x', '?from']] - Initial preconditions
        self.assertEqual(1, 2)

    def test_action_requirements(self):
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.test_tools_path + "Rover/domain2.hddl")
        solver = PartialOrderSolver(domain, problem)
        solver.parameter_selector.presolving_processing(domain, problem)

        # Check action requirements
        self.assertEqual(domain.types['rover'], domain.actions['take_image'].requirements['?r']['type'])
        self.assertEqual({'and': {'calibrated': 2, 'on_board': 2, 'equipped_for_imaging': 1, 'at': 1}},
                         domain.actions['take_image'].requirements['?r']['predicates'])

        self.assertEqual(domain.types['waypoint'], domain.actions['take_image'].requirements['?p']['type'])
        self.assertEqual({'and': {'visible_from': 2, 'at': 2}},
                         domain.actions['take_image'].requirements['?p']['predicates'])

        self.assertEqual(domain.types['objective'], domain.actions['take_image'].requirements['?o']['type'])
        self.assertEqual({'and': {'visible_from': 1}}, domain.actions['take_image'].requirements['?o']['predicates'])

        self.assertEqual(domain.types['camera'], domain.actions['take_image'].requirements['?i']['type'])
        self.assertEqual({'and': {'calibrated': 1, 'on_board': 1, 'supports': 1}},
                         domain.actions['take_image'].requirements['?i']['predicates'])

        self.assertEqual(domain.types['mode'], domain.actions['take_image'].requirements['?m']['type'])
        self.assertEqual({'and': {'supports': 2}}, domain.actions['take_image'].requirements['?m']['predicates'])

    def test_task_method_grounding(self):
        # Check that methods corresponding to a task are being stored correctly
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.rover_path + "rover-domain.hddl")
        t = domain.get_task('calibrate_abs')
        self.assertIn(domain.get_method('m_calibrate_abs_ordering_0'), t.methods)

        t = domain.get_task('empty_store')
        self.assertIn(domain.get_method('m_empty_store_1_ordering_0'), t.methods)
        self.assertIn(domain.get_method('m_empty_store_2_ordering_0'), t.methods)

        t = domain.get_task('get_image_data')
        self.assertIn(domain.get_method('m_get_image_data_ordering_0'), t.methods)

        t = domain.get_task('get_rock_data')
        self.assertIn(domain.get_method('m_get_rock_data_ordering_0'), t.methods)

        t = domain.get_task('get_soil_data')
        self.assertIn(domain.get_method('m_get_soil_data_ordering_0'), t.methods)

        t = domain.get_task('navigate_abs')
        self.assertIn(domain.get_method('m_navigate_abs_1_ordering_0'), t.methods)
        self.assertIn(domain.get_method('m_navigate_abs_2_ordering_0'), t.methods)
        self.assertIn(domain.get_method('m_navigate_abs_3_ordering_0'), t.methods)
        self.assertIn(domain.get_method('m_navigate_abs_4_ordering_0'), t.methods)

        t = domain.get_task('send_image_data')
        self.assertIn(domain.get_method('m_send_image_data_ordering_0'), t.methods)

        t = domain.get_task('send_rock_data')
        self.assertIn(domain.get_method('m_send_rock_data_ordering_0'), t.methods)

        t = domain.get_task('send_soil_data')
        self.assertIn(domain.get_method('m_send_soil_data_ordering_0'), t.methods)

    def test_method_subtask_grounding(self):
        # Check that method subtasks hold reference to action/task not only string
        # rover domain
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.rover_path + "rover-domain.hddl")

        method_keys = list(domain.methods.keys())
        for m in method_keys:
            subtasks = domain.methods[m].subtasks
            if subtasks is not None:
                for t in subtasks.tasks:
                    # print("Method: {}\tSubtask: {}".format(m, t.task))
                    self.assertIsInstance(t.task, Modifier)

    def test_action_effects(self):
        # basic domain
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)
        parser.parse_domain(self.basic_domain_path)

        self.assertEqual(Predicate, type(domain.actions['pickup'].effects.effects[0].predicate))
        self.assertEqual(False, domain.actions['pickup'].effects.effects[0].negated)
        self.assertEqual(Predicate, type(domain.actions['drop'].effects.effects[0].predicate))
        self.assertEqual(True, domain.actions['drop'].effects.effects[0].negated)

    def test_constraint_evaluation(self):
        domain, problem, parser, solver = env_setup(True)
        solver.set_parameter_selector(RequirementSelection)
        parser.parse_domain(self.IPC_Tests_path + "satellite01/domain2.hddl")
        parser.parse_problem(self.IPC_Tests_path + "satellite01/1obs-1sat-1mod.hddl")

        # method0 - (and (not (= ?take_image_instance_4_argument_6 ?turn_to_instance_3_argument_4)))
        method = domain.methods['method0']

        # Test for True
        param_dict = {
            "?take_image_instance_4_argument_6": problem.objects['phenomenon4'],
            "?take_image_instance_4_argument_7": problem.objects['instrument0'],
            "?take_image_instance_4_argument_8": problem.objects['thermograph0'],
            "?turn_to_instance_3_argument_2": problem.objects['satellite0'],
            "?turn_to_instance_3_argument_4": problem.objects['phenomenon6']
        }
        self.assertEqual(True, method._evaluate_constraints(param_dict, None, problem))

        # Test for False
        param_dict['?turn_to_instance_3_argument_4'] = problem.objects['phenomenon4']
        self.assertEqual(False, method._evaluate_constraints(param_dict, None, problem))

    def test_type_satisfaction(self):
        domain, problem, parser, solver = env_setup(True)
        parser.parse_domain(self.IPC_Tests_path + "um-translog01/domain.hddl")
        parser.parse_problem(self.IPC_Tests_path + "um-translog01/problem.hddl")

        # Check that type 'regular_package' satisfies both 'package' and 'regular'
        reg_pack_ob = Object('test_package', domain.types['regular_package'])
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['package'], reg_pack_ob))
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['regular'], reg_pack_ob))
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['regular_package'], reg_pack_ob))

        # Check a child of regular_package also satisfies them both
        food_ob = Object('test_food', domain.types['food'])
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['package'], food_ob))
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['regular'], food_ob))
        self.assertEqual(True, solver.parameter_selector.check_satisfies_type(domain.types['food'], food_ob))

        # Test for false
        self.assertEqual(False, solver.parameter_selector.check_satisfies_type(domain.types['airport'], reg_pack_ob))

    # Ground objects to types? - would make for quicker look-ups in problem.get_objects_of_type()
