import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from runner import Runner
from Internal_Representation.list_parameter import ListParameter


class ListParameterTests(unittest.TestCase):
    JSHOP_block_path = 'Examples/JShop/blocks/'

    def setUp(self) -> None:
        pass

    def test_pop(self):
        mock_list_parameter = ListParameter('?Mocks', '?Mock')
        mock_list_parameter.add_to_list('Mock1')
        mock_list_parameter.add_to_list('Mock2')
        mock_list_parameter.add_to_list('Mock3')
        self.assertEqual('Mock1', mock_list_parameter.pop())
        self.assertEqual('Mock2', mock_list_parameter.pop())
        self.assertEqual('Mock3', mock_list_parameter.pop())
        self.assertIsNone(mock_list_parameter.pop())
