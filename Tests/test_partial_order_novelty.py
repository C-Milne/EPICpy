import unittest.mock
from unittest.mock import patch, MagicMock, Mock, PropertyMock
import os
import sys
import io
import pytest

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Solver.Search_Queues.Novelty_GBFS_Search_Queue_Oldest_First import NoveltyGBFSOldestFirstQueue
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Search_Queues.search_queue_newest_first import SearchQueueNewestFirst
from Solver.Models.default_model import DefaultModel
from Internal_Representation.subtasks import Subtask
from Internal_Representation.state import State
from Internal_Representation.action import Action
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.effects import Effects
from Internal_Representation.precondition import Precondition
from Internal_Representation.conditions import ForAllCondition
from Parsers.HDDL_Parser import HDDLParser


class PartialOrderNoveltySolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.domain = Domain(None)
        self.problem = Problem(self.domain)
        self.domain.add_problem(self.problem)
        self.solver = PartialOrderNoveltySolver(self.domain, self.problem)
        self.parser = HDDLParser(self.domain, self.problem)

    def test_set_search_queue(self):
        self.solver = PartialOrderNoveltySolver(self.domain, self.problem)
        self.solver.set_search_queue(NoveltyGBFSOldestFirstQueue)
        self.assertIsInstance(self.solver.search_models, NoveltyGBFSOldestFirstQueue)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_set_search_queue_warning(self, mock_stdout):
        self.solver = PartialOrderNoveltySolver(self.domain, self.problem)
        with pytest.warns(match="This solver forces the use of Novelty, as such search queue cannot be selected"):
            self.solver.set_search_queue(SearchQueueNewestFirst)
        self.assertIsInstance(self.solver.search_models, NoveltyGBFSQueue)

    def test_expand_action_apply_actions(self):
        self.parser.parse_domain('Examples/Basic/basic.hddl')
        self.parser.parse_problem('Examples/Basic/pb1.hddl')
        self.solver.solve(search=False)

        model = self.solver.search_models.pop()
        subtask = Subtask(self.domain.get_action('drop'), [RegParameter('?a')])
        subtask.add_given_parameters({'?a': self.problem.get_object('kiwi')})
        self.solver._expand_action_apply_actions(subtask, model)
        self.assertEqual(0, len(model.current_state))

    def test_expand_action_apply_actions_no_effects(self):
        self.parser.parse_domain('Examples/Basic/basic.hddl')
        self.parser.parse_problem('Examples/Basic/pb1.hddl')
        self.solver.solve(search=False)

        model = self.solver.search_models.pop()
        mock_action = Action('mock_action', [], None, None)
        self.domain.add_action(mock_action)
        subtask = Subtask(mock_action, [])

        self.solver._expand_action_apply_actions(subtask, model)
        self.assertEqual(1, len(model.current_state))

    @patch('Solver.Models.default_model')
    @patch('Internal_Representation.problem.Problem')
    @patch('Internal_Representation.domain.Domain')
    def test_expand_action_apply_actions_with_For_All_Effect(self, mock_domain, mock_problem, mock_model):
        self.solver = PartialOrderNoveltySolver(mock_domain, mock_problem)
        self.solver._expand_action_apply_forall_effect_novelty = Mock(return_value=1)

        mock_for_all_effect = Mock(spec=Effects.ForAllEffect)
        mock_subtask = Mock(spec=Subtask)
        mock_subtask.get_effects.return_value = [mock_for_all_effect]

        response = self.solver._expand_action_apply_actions(mock_subtask, mock_model)
        self.solver._expand_action_apply_forall_effect_novelty.assert_called_once_with(mock_for_all_effect,
                                                                                       mock_subtask, mock_model, 0)

        self.assertEqual(response, 1)

    @patch('Solver.Models.default_model')
    @patch('Internal_Representation.problem.Problem')
    @patch('Internal_Representation.domain.Domain')
    def test_expand_action_apply_actions_type_error(self, mock_domain, mock_problem, mock_model):
        self.solver = PartialOrderNoveltySolver(mock_domain, mock_problem)
        self.solver._expand_action_apply_forall_effect_novelty = Mock(return_value=1)

        mock_subtask = Mock(spec=Subtask)
        mock_subtask.get_effects.return_value = [Action('Mock Action for Type Error',
                                                        [], None, None)]

        with self.assertRaises(TypeError) as error:
            self.solver._expand_action_apply_actions(mock_subtask, mock_model)
        self.assertEqual('Type \'Action\' is not supported as an effect to apply in this method!', str(error.exception))

    @patch('Solver.Models.default_model')
    @patch('Internal_Representation.problem.Problem')
    @patch('Internal_Representation.domain.Domain')
    def test_expand_action_apply_forall_effect_novelty(self, mock_domain, mock_problem, mock_model):
        self.solver = PartialOrderNoveltySolver(mock_domain, mock_problem)
        mock_for_all_effect = Mock(spec=Effects.ForAllEffect)
        mock_for_all_effect_precondition = Mock(spec=Precondition)
        mock_for_all_effect_precondition_head = Mock(spec=ForAllCondition)

        mock_for_all_effect.get_precondition.return_value = mock_for_all_effect_precondition
        mock_for_all_effect_precondition.get_head.return_value = mock_for_all_effect_precondition_head

        mock_subtask = Mock(spec=Subtask)

        result = self.solver._expand_action_apply_forall_effect_novelty(mock_for_all_effect, mock_subtask, mock_model,
                                                                        0)
        self.assertEqual(1, 2)
