import unittest.mock
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Internal_Representation.modifier import Modifier
from Internal_Representation.precondition import Precondition
from Internal_Representation.reg_parameter import RegParameter


class ModifierTests(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_add_preconditions_twice(self):
        mock_modifier = Modifier('Mock', [])
        mock_preconditions1 = Precondition(['not', ['have', '?a']])
        mock_preconditions2 = Precondition(['not', ['have', '?a']])
        mock_modifier.add_preconditions(mock_preconditions1)

        with self.assertRaises(TypeError) as error:
            mock_modifier.add_preconditions(mock_preconditions2)
        self.assertEqual("Preconditions are already set for this modifier", str(error.exception))

    def test_get_precondition(self):
        mock_preconditions1 = Precondition(['not', ['have', '?a']])
        mock_modifier = Modifier('Mock', [], mock_preconditions1)
        self.assertEqual(mock_preconditions1, mock_modifier.get_precondition())

    def test_get_name(self):
        mock_modifier = Modifier('MockModifier', [])
        self.assertEqual('MockModifier', mock_modifier.get_name())

    def test_get_name_none(self):
        mock_modifier = Modifier('MockModifier', [])
        mock_modifier.name = None
        self.assertEqual('Unknown', mock_modifier.get_name())

    def test_get_parameter_names(self):
        mock_modifier = Modifier('MockModifier', [RegParameter('MockParameter1'),
                                                  RegParameter('MockParameter2'), RegParameter('MockParameter3')])
        self.assertEqual(['MockParameter1', 'MockParameter2', 'MockParameter3'], mock_modifier.get_parameter_names())

    def test_get_parameter_names_resize(self):
        mock_modifier = Modifier('MockModifier', [RegParameter('MockParameter1'),
                                                  RegParameter('MockParameter2')])
        self.assertEqual(['MockParameter1', 'MockParameter2'], mock_modifier.get_parameter_names())
        mock_modifier.add_parameter(RegParameter('MockParameter3'))
        self.assertEqual(['MockParameter1', 'MockParameter2', 'MockParameter3'], mock_modifier.get_parameter_names())

    def test_get_parameter_names_twice(self):
        mock_modifier = Modifier('MockModifier', [RegParameter('MockParameter1'),
                                                  RegParameter('MockParameter2'), RegParameter('MockParameter3')])
        self.assertEqual(['MockParameter1', 'MockParameter2', 'MockParameter3'], mock_modifier.get_parameter_names())
        self.assertEqual(['MockParameter1', 'MockParameter2', 'MockParameter3'], mock_modifier.get_parameter_names())

    def test_collect_parameter_names(self):
        mock_modifier = Modifier('MockModifier', [RegParameter('MockParameter1'),
                                                  RegParameter('MockParameter2'), RegParameter('MockParameter3')])
        self.assertEqual([], mock_modifier.parameter_names)
        mock_modifier._Modifier__collect_parameter_names()
        self.assertEqual(['MockParameter1', 'MockParameter2', 'MockParameter3'], mock_modifier.parameter_names)

    def test_modifier_repr(self):
        mock_modifier = Modifier('MockModifier', [RegParameter('MockParameter1'),
                                                  RegParameter('MockParameter2'), RegParameter('MockParameter3')])
        self.assertEqual('MockModifier', repr(mock_modifier))
