import copy
import sys
import re
from Solver.Heuristics.pruning import Pruning
from Solver.Parameter_Selection.All_Parameters import AllParameters
from Solver.Heuristics.deleteRelaxedUtils.delete_relaxed_requirement_parameter_selector import DeleteRelaxedRequirementSelection
Task = sys.modules['Internal_Representation.task'].Task
Method = sys.modules['Internal_Representation.method'].Method
Action = sys.modules['Internal_Representation.action'].Action
Subtasks = sys.modules['Internal_Representation.subtasks'].Subtasks
Subtask = sys.modules['Internal_Representation.subtasks'].Subtask

if 'Solver.Model' in sys.modules:
    Model = sys.modules['Solver.Models.model'].Model
else:
    from Solver.Models.default_model import DefaultModel

if 'Internal_Representation.domain' in sys.modules:
    Domain = sys.modules['Internal_Representation.domain'].Domain
else:
    from Internal_Representation.domain import Domain

if 'Internal_Representation.problem' in sys.modules:
    Problem = sys.modules['Internal_Representation.problem'].Problem
else:
    from Internal_Representation.problem import Problem

State = sys.modules['Internal_Representation.state'].State
Predicate = sys.modules['Internal_Representation.predicate'].Predicate
RegParameter = sys.modules['Internal_Representation.reg_parameter'].RegParameter
OperatorCondition = sys.modules['Internal_Representation.conditions'].OperatorCondition
PredicateCondition = sys.modules['Internal_Representation.conditions'].PredicateCondition
Precondition = sys.modules['Internal_Representation.precondition'].Precondition
Condition = sys.modules['Internal_Representation.conditions'].Condition
Object = sys.modules['Internal_Representation.Object'].Object
ProblemPredicate = sys.modules['Internal_Representation.problem_predicate'].ProblemPredicate


class AltOperatorCondition(OperatorCondition):
    def __init__(self, operator: str, pred: Predicate):
        super().__init__(operator)
        self.pred = pred    # This is used for 'not' operators

    def _evaluate_children(self, param_dict, search_model, problem):
        children_eval = []
        if len(self.children) > 0 and (self.operator == "and" or self.operator == "or" or self.operator == "="):
            children_eval = [x.evaluate(param_dict, search_model, problem) for x in self.children]
        return children_eval

    def _evaluate_not(self, children_eval, param_dict, search_model, problem):
        assert len(self.children) == 1
        child = self.children[0]
        """Changes go here"""
        if type(child) == AltOperatorCondition or type(child) == OperatorCondition:
            res = False
        else:
            # In the alt state 'not' conditions are stored in the state under new predicates
            # Such as (not-have, kiwi)
            p_list = []
            for i in child.parameter_name:
                p_list.append(param_dict[i])

            res = search_model.current_state.check_if_predicate_value_exists(self.pred, p_list)

        if res:
            return res
        else:
            # Try normal 'not' evaluation
            res = child.evaluate(param_dict, search_model, problem)
            if res is True:
                return False
            else:
                # Add this new predicate to state
                try:
                    search_model.current_state.add_element(ProblemPredicate(self.pred, p_list))
                except Exception as e:
                    # TODO: Investigate this and make a fix
                    return False
                return True


class AltPredicateCondition(PredicateCondition):
    def __init__(self, pred: Predicate, parameter_names: list):
        super().__init__(pred, parameter_names)

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        if self.pred.name != "U":
            p_list = []
            for i in self.parameter_name:
                p_list.append(param_dict[i])

            return search_model.current_state.check_if_predicate_value_exists(self.pred, p_list)
        else:
            if len(self.parameter_name) == 1 and type(self.parameter_name[0]) == str and self.parameter_name[0][0] != "?":
                # Change this to an object
                self.parameter_name = [problem.get_object(self.parameter_name[0])]
            return search_model.current_state.check_if_predicate_value_exists(self.pred, self.parameter_name)


class AltPrecondition(Precondition):
    def __init__(self, conditions: str):
        super().__init__(conditions)

    def add_operator_condition(self, operator: str, parent: Condition, pred: Predicate = None) -> AltOperatorCondition:
        assert type(operator) == str
        assert isinstance(parent, Condition) or parent is None
        assert isinstance(pred, Predicate) or pred is None

        con = AltOperatorCondition(operator, pred)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_predicate_condition(self, pred: Predicate, parameter_names: list, parent: Condition) -> PredicateCondition:
        assert isinstance(parent, Condition) or parent is None
        con = AltPredicateCondition(pred, parameter_names)
        self._final_condition_addition_checks(con, parent)
        return con


class ModelStore:
    def __init__(self, model_num: int):
        self.model_num = model_num
        self.previous_modifiers = []
        self.other_modifiers = []
        self.ranking = None

    def reproduce(self, new_model_num: int) -> 'ModelStore':
        new_model_store = ModelStore(new_model_num)
        new_model_store.previous_modifiers = [x for x in self.previous_modifiers]
        new_model_store.other_modifiers = [x for x in self.other_modifiers]
        new_model_store.ranking = copy.deepcopy(self.ranking)
        return new_model_store


class DeleteRelaxed(Pruning):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)

        self.alt_domain = None
        self.alt_problem = None
        self.all_parameters_selector = AllParameters(self.solver)
        self.requirement_parameters_selector = DeleteRelaxedRequirementSelection(self.solver)
        self.requirement_parameters_selector.presolving_processing(domain, problem)
        self.model_stores = {}
        self._methods_rely_actions = {}     # This stores the methods which rely on each action {Action: {Methods}}
        self._found_actions = set()
        self._found_actions_names = set()
        self._found_methods = set()
        self._found_tasks = set()

    def ranking(self, model: DefaultModel, **kwargs):
        # Create duplicate state
        alt_state = model.current_state.reproduce()

        if len(model.get_progress_tracker().operations_taken) == 0 or type(model.get_progress_tracker().operations_taken[-1].mod) == Action:
            prev_action = True
        else:
            prev_action = False

        if model.model_number not in self.model_stores and model.parent_model_number is not None and \
                model.parent_model_number in self.model_stores:
            self.model_stores[model.model_number] = self.model_stores[model.parent_model_number].reproduce(model.model_number)

        if 'returnAltState' in kwargs:
            return_alt_state = bool(kwargs['returnAltState'])
        else:
            return_alt_state = False

        if model.model_number not in self.model_stores:
            self.model_stores[model.model_number] = ModelStore(model.model_number)
            # Create list with all possible actions and methods
            self.model_stores[model.model_number].previous_modifiers = None

            # Choose target('s)
            targets = self._get_target_tasks(model)
            if return_alt_state:
                res, final_alt_state = self._calculate_distance(self.solver.reproduce_model(model), self.model_stores[model.model_number], alt_state, targets, True)
                self.model_stores[model.model_number].ranking = res
                return res, final_alt_state
            else:
                res = self._calculate_distance(self.solver.reproduce_model(model), self.model_stores[model.model_number], alt_state, targets)
                self.model_stores[model.model_number].ranking = res
                return res
        elif prev_action:
            targets = self._get_target_tasks(model)
            res = self._calculate_distance(self.solver.reproduce_model(model), self.model_stores[model.model_number],
                                           alt_state, targets)
            self.model_stores[model.model_number].ranking = res
            return res
        else:
            return self.model_stores[model.model_number].ranking

    def _get_target_tasks(self, model):
        targets = []
        next_mod = model.search_modifiers[0].task
        if type(next_mod) != Task:
            i = -1
            op = model.get_progress_tracker().operations_taken[i]
            op_task = op.mod
            while type(op_task) != Task:
                i -= 1
                op = model.get_progress_tracker().operations_taken[i]
                op_task = op.mod
            assert type(op_task) == Task
            targets.append("U-" + op_task.name +
                           self._concat_param_object_names([op.parameters_used[x] for x in op.parameters_used]))
        else:
            # We have all tasks
            pass

        for m in model.search_modifiers:
            if type(m.task) == Task:
                targets.append("U-" + m.task.name + self._concat_param_object_names([m.given_params[x] for x in m.given_params]))
        for m in model.waiting_subtasks:
            if type(m.task) == Task:
                targets.append("U-" + m.task.name + self._concat_param_object_names([m.given_params[x] for x in m.given_params]))
        return targets

    def _concat_param_object_names(self, list_obs: list):
        names = ""
        for o in list_obs:
            names += "-" + o.name
        return names

    def _get_objects_from_alt_modifier_name(self, mod, names_only: bool = False) -> list:
        name = mod.name
        obs = []

        num_params_required = len(mod.parameters)
        occurrences = [m.start() for m in re.finditer('-', name)]

        while len(occurrences) >= num_params_required + 1:
            occurrences = occurrences[1:]

        while occurrences:
            start = occurrences.pop(0) + 1
            if occurrences:
                end = occurrences[0]
            else:
                end = len(name)
            if not names_only:
                ob_name = name[start:end]
                o = self.problem.get_object(ob_name)
                if o is None:
                    raise TypeError
                obs.append(o)
            else:
                obs.append(name[start:end])
        return obs

    def _calculate_distance(self, model: DefaultModel, model_store: ModelStore, alt_state: State, targets: list, return_alt_state=False) -> int:
        model.current_state = alt_state
        iteration = 0
        applied_modifiers = []
        found_targets = []
        used_prev_store = False
        self._found_tasks = set()
        self._found_methods = set()
        self._found_actions = set()
        self._found_action_names = set()

        if model_store.previous_modifiers is None:
            # If we have no previous modifiers we need to use requirement selection to determine the objects to use for modifiers
            modifier_selection_mode = True
            modifiers = None
        else:
            modifier_selection_mode = False
            modifiers = [x for x in model_store.previous_modifiers]

        while True:
            iteration += 1
            applicable_modifiers = self._calculate_applicable_modifiers(modifiers, model, modifier_selection_mode, iteration)

            # Add effects of these modifiers to alt_state
            c = -1
            for m in applicable_modifiers:
                c += 1
                given_params = m[1]
                m = m[0]
                if type(m) == Action:
                    self._apply_action(m, model, given_params)
                elif type(m) == Method:
                    self._apply_method(m, model, targets, found_targets)
                else:
                    raise TypeError
                # Remove modifiers from list
                applied_modifiers.append(m)
                if modifiers:
                    del modifiers[modifiers.index(m)]

            # Check exit conditions
            if self._check_targets(targets, found_targets):
                model_store.previous_modifiers = [x for x in applied_modifiers]
                if return_alt_state:
                    return iteration, alt_state
                return iteration
            elif (modifiers and len(modifiers) == 0) and len(model_store.other_modifiers) > 0 and not used_prev_store:
                # TODO: What is going on here???
                modifiers = [x for x in model_store.other_modifiers]
                used_prev_store = True
            elif len(applicable_modifiers) == 0:
                return False

    def _calculate_applicable_modifiers(self, modifiers, model, selection_mode, iteration) -> list:
        if selection_mode:
            return self._calculate_applicable_modifiers_selection_mode(model, iteration > 1)
        else:
            # Iterate mode
            return self._calculate_applicable_modifiers_iterate_mode(modifiers, model)

    def _calculate_applicable_modifiers_selection_mode(self, model, find_methods) -> list:
        # Iterate over all actions in the domain
        applicable_actions = self._calculate_applicable_modifiers_selection_mode_find_actions(model)
        if find_methods:
            # Iterate over all methods in the domain
            applicable_methods = self._calculate_applicable_modifiers_selection_mode_find_methods(model)
        else:
            applicable_methods = []
        return applicable_actions + applicable_methods

    def _calculate_applicable_modifiers_selection_mode_find_actions(self, model) -> list:
        applicable_actions = []
        for action in self.domain.get_all_actions():
            param_options = self.requirement_parameters_selector.get_potential_parameters(action, {}, model)
            for param_option in param_options:
                alt_action_name = self._generate_modifier_alt_name(action, param_option)

                if alt_action_name not in self._found_actions:
                    alt_action = Action(alt_action_name, action.get_parameters(), action.preconditions, action.effects)
                    applicable_actions.append((alt_action, param_option))
                    self._found_actions_names.add(action.name)
        return applicable_actions

    def _calculate_applicable_modifiers_selection_mode_find_methods(self, model) -> list:
        applicable_methods = []
        methods_to_check = self._generate_possible_methods_to_check_selection_mode()
        for method in methods_to_check:
            param_options = self.requirement_parameters_selector.get_potential_parameters(method, {}, model)
            for param_option in param_options:
                # Check if all subtasks have been applied
                applicable = True
                for s in method.subtasks.tasks:
                    required_subtask_name = s.task.name
                    for s_param in s.parameters:
                        required_subtask_name += '-{}'.format(param_option[s_param.name].name)

                    if ProblemPredicate(self.alt_domain.get_predicate('U'), [self.get_create_object(required_subtask_name)]) not in model.current_state:
                        applicable = False
                        break

                if applicable:
                    alt_method_name = self._generate_modifier_alt_name(method, param_option)
                    if alt_method_name not in self._found_methods:
                        alt_method = Method(alt_method_name, method.get_parameters(), method.preconditions,
                                            method.task, method.subtasks, method.constraints)
                        applicable_methods.append((alt_method, param_option))
        return applicable_methods

    def _generate_possible_methods_to_check_selection_mode(self):
        if len(self._found_actions_names) == 0:
            return set()
        elif len(self._found_actions_names) == 1:
            return self._methods_rely_actions[next(iter(self._found_actions_names))]
        union_elements = [self._methods_rely_actions[a] for a in self._found_actions_names]
        return_methods = set().union(*union_elements)
        return return_methods

    def _generate_modifier_alt_name(self, modifier, given_params):
        alt_name = modifier.name
        for p in modifier.parameters:
            alt_name += "-{}".format(given_params[p.name].name)
        return alt_name

    def _calculate_applicable_modifiers_iterate_mode(self, modifiers, model) -> list:
        # Find all modifiers which can be applied
        applicable_modifiers = []
        for m in modifiers:
            given_params = {}
            obs = self._get_objects_from_alt_modifier_name(m)
            params = m.get_parameters()
            for i in range(len(params)):
                given_params[params[i].name] = obs[i]
            if m.evaluate_preconditions(model, given_params, self.alt_problem):
                applicable_modifiers.append((m, copy.copy(given_params)))
        return applicable_modifiers

    def _apply_action(self, m, model, given_params):
        for e in m.effects.effects:
            if e.negated:
                pred = self.alt_domain.get_predicate("not_" + e.predicate.name)
                model.current_state.add_element(
                    ProblemPredicate(pred, [given_params[x] for x in e.parameters]))
            else:
                model.current_state.add_element(ProblemPredicate(e.predicate, [given_params[x] for x in e.parameters]))

        # Add action name to state (U-actionName)
        prob_pred = ProblemPredicate(self.alt_domain.get_predicate("U"), [self.get_create_object(m.name)])
        model.current_state.add_element(prob_pred, False)
        self._found_actions.add(m.name)

    def _apply_method(self, m, model, targets, found_targets):
        # Add the name of the method to the state
        method_name = m.name
        method_name_ob = self.alt_problem.get_object(method_name)
        if method_name_ob is None:
            method_name_ob = Object(method_name)
            self.alt_problem.add_object(method_name_ob)
        method_prob_pred = ProblemPredicate(self.alt_domain.get_predicate("U"), [method_name_ob])
        model.current_state.add_element(method_prob_pred, False)
        self._found_methods.add(method_name)

        # Check if name of task this method expands is already in state
        ob_names = self._get_objects_from_alt_modifier_name(m, True)
        task_name = m.task['task'].name

        for param_name in m.task['params']:
            try:
                i_params = 0
                l_params = len(m.parameters)
                found = False
                while i_params < l_params:
                    if m.parameters[i_params].name == param_name.name:
                        found = True
                        break
                    i_params += 1
                if not found:
                    raise NameError
                task_name += "-" + ob_names[i_params]
            except Exception as e:
                raise TypeError

        if task_name not in self._found_tasks:
            task_name_ob = self.alt_problem.get_object(task_name)
            if task_name_ob is None:
                self.alt_problem.add_object(Object(task_name))
                task_name_ob = self.alt_problem.get_object(task_name)
            prob_pred = ProblemPredicate(self.alt_domain.get_predicate("U"), [task_name_ob])
            model.current_state.add_element(prob_pred, False)
            # Check if prob_pred in targets
            task_string = str(prob_pred).replace(" ", "")
            if task_string in targets:
                found_targets.append(task_string)
            self._found_tasks.add(task_name)

    def get_create_object(self, ob_name):
        if ob_name in self.alt_problem.objects:
            return self.alt_problem.objects[ob_name]
        ob = Object(ob_name)
        self.alt_problem.add_object(ob)
        return ob

    def _check_targets(self, targets: list, found_targets: list) -> bool:
        if len(targets) == len(found_targets):
            return True
        return False

    def presolving_processing(self, **kwargs) -> None:
        self.alt_domain = Domain(None)
        self.alt_problem = Problem(self.alt_domain)
        self.alt_domain.add_problem(self.alt_problem)
        # Create new domain
        self._generate_alt_domain()
        self._generate_alt_problem()

    def _generate_alt_domain(self):
        # Give alt domain types
        self.alt_domain.types = self.domain.types

        # Give alt domain predicates
        for p in self.domain.predicates:
            pred = self.domain.predicates[p]
            self.alt_domain.add_predicate(pred)
            self.alt_domain.add_predicate(Predicate("not_" + p, pred.parameters))
        self.alt_domain.add_predicate(Predicate("U", [RegParameter("?action")]))

        self._map_actions_to_methods()
    def _map_actions_to_methods(self):
        for m in self.domain.get_all_methods():
            for subtask in m.subtasks.tasks:
                if type(subtask.task) == Action:
                    self._add_to_methods_actions_mapping(subtask.task, m)

    def _add_to_methods_actions_mapping(self, action, method):
        if action.name not in self._methods_rely_actions.keys():
            self._methods_rely_actions[action.name] = {method}
        else:
            self._methods_rely_actions[action.name].add(method)

    def _generate_alt_preconditions(self, precondition):
        alt_precon = AltPrecondition(str(precondition.conditions))
        alt_precon_head = self._generate_alt_preconditions_recur(precondition.head)
        alt_precon.head = alt_precon_head
        return alt_precon

    def _generate_alt_preconditions_recur(self, condition):
        if type(condition) == OperatorCondition:
            alt_condition = AltOperatorCondition(condition.operator, None)
            alt_condition.children = [self._generate_alt_preconditions_recur(c) for c in condition.children]
            return alt_condition
        elif type(condition) == PredicateCondition:
            alt_condition = AltPredicateCondition(condition.pred, condition.parameter_name)
            alt_condition.set_parent(condition.parent)
            return alt_condition
        else:
            raise NotImplementedError

    def _generate_alt_problem(self):
        self.alt_problem.initial_state = self.problem.initial_state.reproduce()

        # Get objects
        obs = self.problem.get_all_objects()
        for o in obs:
            self.alt_problem.add_object(obs[o])
