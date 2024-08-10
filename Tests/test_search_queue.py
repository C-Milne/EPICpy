import unittest
from unittest.mock import Mock, MagicMock
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Solver.Search_Queues.search_queue import SearchQueue
from Internal_Representation.Type import Type
from Solver.Models.model import Model
from Solver.Heuristics.Heuristic import Heuristic


class SearchQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.search_queue = SearchQueue()

    def test_add_incorrect_param_type(self):
        """Pass an object which is not an instance of class Model.
        We expect an error in this case"""
        mockType = Type("MockType")
        with self.assertRaises(TypeError) as context:
            self.search_queue.add(mockType)

        self.assertEqual(('Invalid parameter type!\n'
 "Expected Model got <class 'Internal_Representation.Type.Type'>"), context.exception.args[0])

    def test_clear_completed_models(self):
        mockModel = Mock(spec=Model)
        self.search_queue._add_completed_model(mockModel)
        self.search_queue._add_completed_model(mockModel)
        self.search_queue._add_completed_model(mockModel)
        self.assertEqual(3, self.search_queue.get_num_completed_models())
        self.search_queue.clear_completed_models()
        self.assertEqual(0, self.search_queue.get_num_completed_models())

    def test_pop_empty_queue(self):
        self.assertIsNone(self.search_queue.pop())

    def test_get_model_list(self):
        mockHeuristic = Mock(spec=Heuristic)
        mockHeuristic.ranking.return_value = 3
        self.search_queue.add_heuristic(mockHeuristic)
        self.search_queue._calc_ranking = Mock(return_value=5)

        mockModel = Mock(spec=Model)
        mockModel.get_num_search_modifiers.return_value = 2
        self.search_queue.add(mockModel)
        mockModel.__lt__ = Mock(return_value=True)
        mockModel.__gt__ = Mock(return_value=True)

        mockModel2 = Mock(spec=Model)
        mockModel2.get_num_search_modifiers.return_value = 5
        self.search_queue.add(mockModel2)
        mockModel2.__lt__ = Mock(return_value=True)
        mockModel2.__gt__ = Mock(return_value=True)

        mockModel3 = Mock(spec=Model)
        mockModel3.get_num_search_modifiers.return_value = 3
        self.search_queue.add(mockModel3)
        mockModel3.__lt__ = Mock(return_value=True)
        mockModel3.__gt__ = Mock(return_value=True)

        models = self.search_queue.get_model_list()
        self.assertIn(mockModel, models)
        self.assertIn(mockModel2, models)
        self.assertIn(mockModel3, models)
