from Solver.Solving_Algorithms.solver import Solver
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver
from Internal_Representation.domain import Domain
from Internal_Representation.problem import Problem
from Parsers.HDDL_Parser import HDDLParser


def setup() -> [Domain, Problem, Solver]:
    domain = Domain(None)
    problem = Problem(domain)
    domain.add_problem(problem)

    parser = HDDLParser(domain, problem)
    parser.parse_domain("../Examples/IPC_Tests/Rover/rover-domain.hddl")
    parser.parse_problem("../Examples/IPC_Tests/Rover/pfile01.hddl")

    # Initialise solver
    solver = PartialOrderSolver(domain, problem)
    return domain, problem, solver


def execution_prep(problem, solver) -> None:
    solver.solve(search=False)
