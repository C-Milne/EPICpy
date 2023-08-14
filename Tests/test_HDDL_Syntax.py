import unittest
import os
import sys

current_dir = os.getcwd()
if current_dir.endswith('Tests'):
    os.chdir('..')
    sys.path.append(os.getcwd())

from Parsers.HDDL_Parser import HDDLParser
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem


class HDDLTests(unittest.TestCase):

    def setUp(self) -> None:
        self.basic_domain_path = "../Examples/Basic/basic.hddl"
        self.basic_pb1_path = "../Examples/Basic/pb1.hddl"
        self.basic_pb1_path_SHOP = "../Examples/Basic/pb1.shop"
        self.test_tools_path = "Tests/TestTools/"
        self.blocksworld_path = "../Examples/Blocksworld/"
        self.rover_path = "../Examples/IPC_Tests/Rover/"

    def test_method_same_name(self):
        """Test setting methods with same name"""
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)

        with self.assertRaises(Exception) as error:
            parser.parse_domain(self.test_tools_path + "basic/basic_domain_test_1.hddl")
        self.assertEqual("Method Name 'swap_ob_1' is Already Assigned", str(error.exception))

    def test_modify_method_task(self):
        """Test setting method task after it has already been set.
        In the file developed for this test, the method 'have_first' has its 'task' attribute set twice"""
        domain = Domain(None)
        problem = Problem(domain)
        domain.add_problem(problem)

        parser = HDDLParser(domain, problem)

        with self.assertRaises(AttributeError) as error:
            parser.parse_domain(self.test_tools_path + "basic/basic_domain_test_2.hddl")
        self.assertEqual("Attribute 'Task' has Already been set for the Method throw. Please check your domain file.",
                         str(error.exception).replace("\"", ""))
