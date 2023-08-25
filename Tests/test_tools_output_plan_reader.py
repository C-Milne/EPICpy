import unittest
import unittest.mock
from unittest.mock import patch
import os
import sys
import io

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Tools.output_plan_reader import read_plan, display_plan
from Tests.TestTools.env_setup import env_setup
from runner import Runner
from Solver.Models.model import Model


class OutputPlanReaderTests(unittest.TestCase):
    basic_path = 'Examples/Basic/'

    def setUp(self) -> None:
        Model.model_counter = 0

    def tearDown(self) -> None:
        if os.path.exists('output/test_read_plan.pickle'):
            os.remove('output/test_read_plan.pickle')

    def test_read_plan(self):
        controller = Runner(self.basic_path + 'basic.hddl', self.basic_path + 'pb1.hddl')
        controller.parse_domain()
        controller.parse_problem()
        result = controller.solve()
        controller.output_result_file(result, 'test_read_plan.pickle')

        read_result = read_plan('output/test_read_plan.pickle')
        self.assertTrue(read_result.equality_check(result))

    def test_read_plan_error(self):
        with self.assertRaises(IOError) as error:
            read_plan('output/test_read_plan.pickle')
        self.assertEqual("File output/test_read_plan.pickle could not be found", str(error.exception))

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_display_plan(self, mock_stdout):
        controller = Runner(self.basic_path + 'basic.hddl', self.basic_path + 'pb1.hddl')
        controller.parse_domain()
        controller.parse_problem()
        result = controller.solve()

        display_plan(result)
        self.assertEqual("""
Actions Taken:
drop - kiwi
pickup - banjo

Operations Taken:
swap - banjo kiwi
have_second - banjo kiwi
drop - kiwi
pickup - banjo

Search Models Created During Search: 3
""", mock_stdout.getvalue())
