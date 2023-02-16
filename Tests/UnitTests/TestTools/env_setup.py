from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Parsers.HDDL_Parser import HDDLParser
from Parsers.JSHOP_Parser import JSHOPParser
from Parsers.parser import Parser
from Solver.Solving_Algorithms.solver import Solver
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Solver.Solving_Algorithms.total_order import TotalOrderSolver
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Solver.Solving_Algorithms.partial_order_novelty_no_reset import PartialOrderNoveltyNoResetSolver


def env_setup(HDDL: bool, partial_order: bool = True, **kwargs) -> [Domain, Problem, Parser, PartialOrderSolver]:
    domain = Domain(None)
    problem = Problem(domain)
    domain.add_problem(problem)
    if HDDL:
        parser = HDDLParser(domain, problem)
    else:
        parser = JSHOPParser(domain, problem)

    if 'solver' not in kwargs:
        if partial_order:
            solver = PartialOrderSolver(domain, problem)
        else:
            solver = TotalOrderSolver(domain, problem)
    else:
        solver_code = int(kwargs['solver'])
        if solver_code == 1:
            solver = PartialOrderNoveltySolver(domain, problem)
        elif solver_code == 2:
            solver = PartialOrderNoveltyNoResetSolver(domain, problem)
        else:
            raise ValueError('Unknown solver code: {}'.format(solver_code))

    return domain, problem, parser, solver


def solver_setup(solver: Solver, problem: Problem) -> None:
    solver.solve(search=False)
