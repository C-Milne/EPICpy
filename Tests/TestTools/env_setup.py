import os
import sys

current_dir = os.getcwd()
# print(current_dir)
if current_dir.endswith('EPICpy/Tests'):
    os.chdir('../')
    sys.path.append(os.getcwd())
    os.chdir(current_dir)
# print(os.getcwd())

from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Parsers.HDDL_Parser import HDDLParser
from Parsers.JSHOP_Parser import JSHOPParser
from Parsers.parser import Parser
from Solver.Solving_Algorithms.solver import Solver
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Solver.Solving_Algorithms.partial_order_novelty_no_reset import PartialOrderNoveltyNoResetSolver
from Solver.Solving_Algorithms.partial_order_novelty_level_2 import PartialOrderNoveltyLevelTwoSolver
from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection
from Solver.Models.model import Model
from Solver.Models.default_model import DefaultModel


def env_setup(HDDL: bool, **kwargs) -> [Domain, Problem, Parser, PartialOrderSolver]:
    domain = Domain(None)
    problem = Problem(domain)
    domain.add_problem(problem)

    if HDDL:
        parser = HDDLParser(domain, problem)
    else:
        parser = JSHOPParser(domain, problem)

    if 'solver' not in kwargs:
        solver = PartialOrderSolver(domain, problem)
    else:
        solver_code = int(kwargs['solver'])
        if solver_code == 1:
            solver = PartialOrderNoveltySolver(domain, problem)
        elif solver_code == 2:
            solver = PartialOrderNoveltyNoResetSolver(domain, problem)
        elif solver_code == 3:
            solver = PartialOrderNoveltyLevelTwoSolver(domain, problem)
        elif solver_code == 4:
            solver = PartialOrderNoveltyMethodsSolver(domain, problem)
        else:
            raise ValueError('Unknown solver code: {}'.format(solver_code))

    if 'parameter_selector' in kwargs:
        param_selector_code = int(kwargs['parameter_selector'])
        if param_selector_code == 1:
            solver.set_parameter_selector(RequirementSelection)
        else:
            raise ValueError('Unknown parameter selector code: {}'.format(param_selector_code))

    if 'model_class' in kwargs:
        raise NotImplementedError
    else:
        solver.set_model_class(DefaultModel)

    Model.model_counter = 0
    return domain, problem, parser, solver


def solver_setup(solver: Solver, problem: Problem) -> None:
    solver.solve(search=False)
