import unittest
from Tests.UnitTests.TestTools.env_setup import env_setup
from Parsers.JSHOP_Parser import JSHOPParser
from Internal_Representation.list_parameter import ListParameter
from Internal_Representation.reg_parameter import RegParameter


class JSHOPParsingTests(unittest.TestCase):

    def setUp(self) -> None:
        self.basic_path = "../Examples/JShop/basic/"
        self.block_path = "../Examples/JShop/blocks/"
        # self.block_path = "Tests/Examples/JShop/blocks/"
        self.forall_path = "../Examples/JShop/forall/"
        self.rover_test_path = "TestTools/J-Rover/"
        self.rover_path = "../Examples/JShop/rover/"

    def test_parsing_basic_domain(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.basic_path + "basic.jshop")

        self.assertEqual(1, len(domain.predicates))
        self.assertIn('have', domain.predicates)
        self.assertEqual(1, len(domain.predicates['have'].parameters))

        self.assertEqual(2, len(domain.actions))
        self.assertIn('!pickup', domain.actions)
        self.assertIn('!drop', domain.actions)

        self.assertEqual(1, len(domain.actions['!pickup'].parameters))
        self.assertEqual('?a', domain.actions['!pickup'].parameters[0].name)
        self.assertEqual(None, domain.actions['!pickup'].parameters[0].type)
        self.assertEqual([], domain.actions['!pickup'].preconditions.conditions)
        self.assertEqual(1, len(domain.actions['!pickup'].effects.effects))
        self.assertEqual(False, domain.actions['!pickup'].effects.effects[0].negated)
        self.assertEqual(['?a'], domain.actions['!pickup'].effects.effects[0].parameters)
        self.assertEqual(domain.predicates['have'], domain.actions['!pickup'].effects.effects[0].predicate)

        self.assertEqual(1, len(domain.actions['!drop'].parameters))
        self.assertEqual('?a', domain.actions['!drop'].parameters[0].name)
        self.assertEqual(None, domain.actions['!drop'].parameters[0].type)
        self.assertEqual(['and', ['have', '?a']], domain.actions['!drop'].preconditions.conditions)
        self.assertEqual(1, len(domain.actions['!drop'].effects.effects))
        self.assertEqual(True, domain.actions['!drop'].effects.effects[0].negated)
        self.assertEqual(['?a'], domain.actions['!drop'].effects.effects[0].parameters)
        self.assertEqual(domain.predicates['have'], domain.actions['!drop'].effects.effects[0].predicate)

        self.assertEqual(1, len(domain.tasks))
        self.assertIn('swap', domain.tasks)
        self.assertEqual(2, len(domain.tasks['swap'].methods))
        self.assertIn(domain.methods['method0'], domain.tasks['swap'].methods)
        self.assertIn(domain.methods['method1'], domain.tasks['swap'].methods)
        self.assertEqual(2, len(domain.tasks['swap'].parameters))
        self.assertEqual('?x', domain.tasks['swap'].parameters[0].name)
        self.assertEqual(None, domain.tasks['swap'].parameters[0].type)
        self.assertEqual('?y', domain.tasks['swap'].parameters[1].name)
        self.assertEqual(None, domain.tasks['swap'].parameters[1].type)

        self.assertEqual(2, len(domain.methods))
        self.assertIn('method0', domain.methods)
        self.assertEqual(['and', ['have', '?x'], ['not', ['have', '?y']]], domain.methods['method0'].preconditions.conditions)
        self.assertIn('method1', domain.methods)
        self.assertEqual(['and', ['have', '?y'], ['not', ['have', '?x']]], domain.methods['method1'].preconditions.conditions)

    def test_parsing_basic_problem(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.basic_path + "basic.jshop")
        parser.parse_problem(self.basic_path + "problem.jshop")

        self.assertIn("kiwi", problem.objects)
        self.assertIn("banjo", problem.objects)
        self.assertEqual(2, len(problem.objects))

        self.assertEqual(1, len(problem.initial_state.elements))
        self.assertEqual(domain.predicates['have'], problem.initial_state.elements[0].predicate)
        self.assertEqual(1, len(problem.initial_state.elements[0].objects))
        self.assertEqual(problem.objects['kiwi'], problem.initial_state.elements[0].objects[0])

        self.assertEqual(1, len(problem.subtasks.tasks))
        self.assertEqual(domain.tasks['swap'], problem.subtasks.tasks[0].task)
        self.assertEqual(2, len(problem.subtasks.tasks[0].parameters))
        self.assertEqual(problem.objects['banjo'], problem.subtasks.tasks[0].parameters[0])
        self.assertEqual(problem.objects['kiwi'], problem.subtasks.tasks[0].parameters[1])

    def test_parsing_blocks_domain(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.block_path + "blocks.jshop")

        self.assertEqual(10, len(domain.tasks))
        assertGoalTask = domain.tasks['assert-goals']
        self.assertEqual([], assertGoalTask.methods)
        self.assertEqual([], assertGoalTask.parameters)
        self.assertEqual(None, assertGoalTask.preconditions)
        self.assertEqual(2, len(assertGoalTask.tasks))

        self.assertEqual(1, len(assertGoalTask.tasks[0].parameters))
        self.assertEqual(ListParameter, type(assertGoalTask.tasks[0].parameters[0]))
        self.assertEqual('?goal', assertGoalTask.tasks[0].parameters[0].internal_param_name)
        self.assertEqual('?goals', assertGoalTask.tasks[0].parameters[0].name)
        self.assertEqual([], assertGoalTask.tasks[0].tasks)

        self.assertEqual([], assertGoalTask.tasks[1].parameters)
        self.assertEqual(1, len(assertGoalTask.tasks[1].methods))
        self.assertEqual([], assertGoalTask.tasks[1].methods[0].parameters)
        self.assertEqual([], assertGoalTask.tasks[1].methods[0].preconditions.conditions)
        self.assertEqual([], assertGoalTask.tasks[1].tasks)

        # Check predicates
        self.assertEqual(8, len(domain.predicates))
        self.assertIn('clear', domain.predicates)
        self.assertIn('on-table', domain.predicates)
        self.assertIn('holding', domain.predicates)
        self.assertIn('on', domain.predicates)
        self.assertIn('block', domain.predicates)
        self.assertIn('dont-move', domain.predicates)
        self.assertIn('put-on-table', domain.predicates)
        self.assertIn('stack-on-block', domain.predicates)

        # Check axioms
        self.assertEqual(2, len(domain.derived_predicates))
        self.assertIn('same', domain.derived_predicates)
        self.assertIn('need-to-move', domain.derived_predicates)
        self.assertEqual(2, len(domain.derived_predicates['same'].parameters))
        self.assertEqual('?x', domain.derived_predicates['same'].parameters[0].name)
        self.assertEqual('?x', domain.derived_predicates['same'].parameters[1].name)

        self.assertEqual(1, len(domain.derived_predicates['need-to-move'].parameters))
        self.assertEqual('?x', domain.derived_predicates['need-to-move'].parameters[0].name)

    def test_parsing_blocks_problem(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.block_path + "blocks.jshop")
        parser.parse_problem(self.block_path + "problem.jshop")

        self.assertEqual(300, len(problem.objects))
        for i in range(1, 301):
            self.assertIn("b" + str(i), problem.objects)

        self.assertEqual(1, len(problem.subtasks.tasks))
        self.assertEqual(domain.tasks['achieve-goals'], problem.subtasks.tasks[0].task)
        self.assertEqual(ListParameter, type(problem.subtasks.tasks[0].parameters))

    def test_parsing_task_finding_parameters(self):
        # When parsing a task with methods, check that parameters not defined in the heading but found in the
        # preconditions/effects are found
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_path + "forall.jshop")
        solver.parameter_selector.presolving_processing(domain, problem)

        method = domain.methods['method0']
        self.assertIn('?x', [p.name for p in method.parameters])
        self.assertIn('?y', [p.name for p in method.parameters])
        self.assertIn('?t', [p.name for p in method.parameters])
        self.assertEqual(3, len(method.parameters))

    def test_parsing_method_subtask(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.forall_path + "forall.jshop")

        self.assertEqual([RegParameter('?x'), RegParameter('?t')], domain.methods['method0'].subtasks.tasks[0].parameters)

        parser.parse_problem(self.forall_path + "problem.jshop")

        self.assertEqual([RegParameter('?x'), RegParameter('?t')],
                         domain.methods['method0'].subtasks.tasks[0].parameters)

    def test_parsing_subtask_method_selection(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_test_path + "rover.jshop")

        method = domain.tasks['navigate'].tasks[0]
        req_method = domain.tasks['navigate'].tasks[1]

        self.assertEqual(1, len(method.methods))
        method = method.methods[0]
        self.assertEqual(3, len(method.subtasks.tasks[1].task.parameters))

    def test_parsing_rover_pb1(self):
        domain, problem, parser, solver = env_setup(False)
        parser.parse_domain(self.rover_path + "rover.jshop")
        parser.parse_problem(self.rover_path + "pb1.jshop")
        self.assertEqual(1, len(problem.subtasks.task_orderings))
        self.assertEqual(3, len(problem.subtasks.task_orderings[0]))
