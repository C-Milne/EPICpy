import os
import pickle
import re
import copy
from typing import List
from runner import Runner
from Internal_Representation.action import Action
from Solver.Models.model import Model
from Solver.Parameter_Selection.All_Parameters import AllParameters
from Solver.Heuristics.delete_relaxed import DeleteRelaxed
from Internal_Representation.state import State
from Internal_Representation.problem_predicate import ProblemPredicate
"""This file is used to calculate the size of a parsed problem.
The results are stored in a common pickled dictionary."""
global pickle_file_name
pickle_file_name = "problem_sizes.pickle"


def calculate_size(domain_file: str, problem_file: str, file_path=pickle_file_name) -> int:
    global pickle_file_name
    pickle_file_name = file_path

    controller = Runner(domain_file, problem_file)
    controller.parse_domain()
    controller.parse_problem()

    size = _calculate_domain_size(controller) + _calculate_problem_size(controller)
    # size = _calculate_predicate_state_size(controller)

    size_dict = _open_pickled_dictionary()

    indexes = [_.start() for _ in re.finditer("/", problem_file)]
    problem_name = problem_file[indexes[-2] + 1:]

    size_dict[problem_name] = size
    _write_pickled_dictionary(size_dict)
    return size


class DeleteRelaxedTotalPredicates(DeleteRelaxed):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)

    def _calculate_distance(self, model: Model, alt_state: State) -> int:
        all_actions = [self.alt_domain.actions[a] for a in self.alt_domain.actions]
        prev_num_preds = 0
        applied_actions = []

        while True:
            """Get applicable actions"""
            applicable_actions = []
            for a in all_actions:
                given_params = {}
                obs = self._get_objects_from_alt_modifier_name(a.name)
                params = a.get_parameters()
                for i in range(len(params)):
                    given_params[params[i].name] = obs[i]
                if a.evaluate_preconditions(model, given_params, self.alt_problem):
                    applicable_actions.append((a, copy.copy(given_params)))

            """Add effects of actions to alt_state"""
            for a in applicable_actions:
                given_params = a[1]
                a = a[0]
                for e in a.effects.effects:
                    if e.negated:
                        pred = self.alt_domain.get_predicate("not_" + e.predicate.name)
                        model.current_state.add_element(
                            ProblemPredicate(pred, [given_params[x] for x in e.parameters]))
                    else:
                        model.current_state.add_element(
                            ProblemPredicate(e.predicate, [given_params[x] for x in e.parameters]))
                """Remove action from list"""
                applied_actions.append(a)
                del all_actions[all_actions.index(a)]

            """Check exit conditions"""
            if len(model.current_state) == prev_num_preds:
                break
            prev_num_preds = len(model.current_state)
        return 2 ** len(applied_actions)


def _calculate_predicate_state_size(controller: Runner) -> int:
    size_calculator = DeleteRelaxedTotalPredicates(controller.domain, controller.problem, controller.solver, [])
    size_calculator.presolving_processing()

    model = Model(controller.problem.initial_state, [])
    res = size_calculator._calculate_distance(model, State.reproduce(model.current_state))
    return res


def __create_alt_actions(controller: Runner) -> List[Action]:
    controller.solver.set_parameter_selector(AllParameters)
    # Get list of alt-actions
    alt_actions = []
    for a in controller.domain.get_all_actions():
        # Consider action with all possible parameters
        param_options = controller.solver.parameter_selector.get_potential_parameters(a, {}, None)
        for params in param_options:
            concat_param_names = ""
            for p in params:
                concat_param_names += "-" + params[p].name
            alt_name = a.name + concat_param_names
            alt_precons = a.get_precondition()
            alt_effects = copy.deepcopy(a.get_effects())
            alt_a = Action(alt_name, a.get_parameters(), alt_precons, alt_effects)
            alt_actions.append(alt_a)
    return alt_actions


def _calculate_domain_size(controller: Runner) -> int:
    domain_size = 0

    domain_size += len(controller.domain.predicates)
    domain_size += len(controller.domain.types)

    for t in controller.domain.tasks:
        t = controller.domain.tasks[t]
        domain_size += 1
        if t.parameters is not None:
            domain_size += len(t.parameters)

    for m in controller.domain.methods:
        m = controller.domain.methods[m]
        domain_size += 1
        if m.parameters is not None:
            domain_size += len(m.parameters)
        if m.subtasks is not None:
            domain_size += len(m.subtasks)
        if m.preconditions is not None:
            domain_size += len(m.preconditions)
        if m.constraints is not None:
            domain_size += len(m.constraints)

    for a in controller.domain.actions:
        a = controller.domain.actions[a]
        domain_size += 1
        if a.parameters is not None:
            domain_size += len(a.parameters)
        if a.preconditions is not None:
            domain_size += len(a.preconditions)
        if a.effects is not None:
            domain_size += len(a.effects)

    return domain_size


def _calculate_problem_size(controller: Runner) -> int:
    problem_size = 0

    problem_size += len(controller.problem.objects)
    if controller.problem.goal_conditions is not None:
        problem_size += len(controller.problem.goal_conditions)
    problem_size += (len(controller.problem.subtasks) * 10)
    problem_size += len(controller.problem.initial_state)
    return problem_size


def _open_pickled_dictionary() -> dict:
    """If pickle file does not exist, return an empty dict"""
    if os.path.exists(pickle_file_name):
        # Open and return the dictionary
        with open(pickle_file_name, 'rb') as handle:
            size_dict = pickle.load(handle)
        return size_dict
    return {}


def _write_pickled_dictionary(size_dict) -> None:
    with open(pickle_file_name, 'wb') as handle:
        pickle.dump(size_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
