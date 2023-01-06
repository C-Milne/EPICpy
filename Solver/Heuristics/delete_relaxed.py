import copy
import sys
import re
from Solver.Heuristics.pruning import Pruning
from Solver.Parameter_Selection.All_Parameters import AllParameters
Task = sys.modules['Internal_Representation.task'].Task
Method = sys.modules['Internal_Representation.method'].Method
Action = sys.modules['Internal_Representation.action'].Action
Subtasks = sys.modules['Internal_Representation.subtasks'].Subtasks
Subtask = sys.modules['Internal_Representation.subtasks'].Subtasks.Subtask

if 'Solver.Model' in sys.modules:
    Model = sys.modules['Solver.Models.model'].Model
else:
    from Solver.Models.model import Model

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

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        children_eval = []
        if len(self.children) > 0 and (self.operator == "and" or self.operator == "or" or self.operator == "="):
            children_eval = [x.evaluate(param_dict, search_model, problem) for x in self.children]
        if self.operator == "and":
            for i in children_eval:
                if i != True:
                    return False
            return True
        elif self.operator == "or":
            for i in children_eval:
                if i == True:
                    return True
            return False
        elif self.operator == "not":
            assert len(self.children) == 1
            """Changes go here"""
            if type(self.children[0]) == AltOperatorCondition or type(self.children[0]) == OperatorCondition:
                res = False
            else:
                # In the alt state not conditions are stored in the state under new predicates
                # Such as (not-have, kiwi)
                p_list = []
                for i in self.children[0].parameter_name:
                    p_list.append(param_dict[i])

                res = search_model.current_state.check_if_predicate_value_exists(self.pred, p_list)
            if res:
                return res
            else:
                # Try normal not evaluation
                res = self.children[0].evaluate(param_dict, search_model, problem)
                if res is True:
                    return False
                else:
                    # Add this new predicate to state
                    try:
                        search_model.current_state.add_element(ProblemPredicate(self.pred, p_list))
                    except Exception as e:
                        return False
                    return True
        elif self.operator == "=":
            v = children_eval[0]
            for i in children_eval[1:]:
                if v != i:
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
        self.parameter_selector = AllParameters(self.solver)
        self.model_stores = {}

    def ranking(self, model: Model) -> float:
        # Create duplicate state
        alt_state = State.reproduce(model.current_state)

        if len(model.get_progress_tracker().operations_taken) == 0 or type(model.get_progress_tracker().operations_taken[-1].mod) == Action:
            prev_action = True
        else:
            prev_action = False

        if model.model_number not in self.model_stores and model.parent_model_number is not None and \
                model.parent_model_number in self.model_stores:
            self.model_stores[model.model_number] = self.model_stores[model.parent_model_number].reproduce(model.model_number)

        if model.model_number not in self.model_stores:
            self.model_stores[model.model_number] = ModelStore(model.model_number)
            # Create list with all possible actions and methods
            for a in self.alt_domain.get_all_actions():
                self.model_stores[model.model_number].previous_modifiers.append(a)
            for m in self.alt_domain.get_all_methods():
                self.model_stores[model.model_number].previous_modifiers.append(m)

            # Choose target('s)
            targets = self._get_target_tasks(model)
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

    def _calculate_distance(self, model: Model, model_store: ModelStore, alt_state: State, targets: list) -> int:
        model.current_state = alt_state
        iteration = 0
        modifiers = [x for x in model_store.previous_modifiers]
        applied_modifiers = []
        found_targets = []
        used_prev_store = False
        while True:
            iteration += 1
            applicable_modifiers = []
            # Find all modifiers which can be applied
            for m in modifiers:
                given_params = {}
                obs = self._get_objects_from_alt_modifier_name(m)
                params = m.get_parameters()
                for i in range(len(params)):
                    given_params[params[i].name] = obs[i]
                if m.evaluate_preconditions(model, given_params, self.alt_problem):
                    applicable_modifiers.append((m, copy.copy(given_params)))

            # Add effects of these modifiers to alt_state
            c = -1
            for m in applicable_modifiers:
                c += 1
                given_params = m[1]
                m = m[0]
                if type(m) == Action:
                    for e in m.effects.effects:
                        if e.negated:
                            pred = self.alt_domain.get_predicate("not_" + e.predicate.name)
                            model.current_state.add_element(
                                ProblemPredicate(pred, [given_params[x] for x in e.parameters]))
                        else:
                            model.current_state.add_element(ProblemPredicate(e.predicate, [given_params[x] for x in e.parameters]))

                    # Add action name to state (U-actionName)
                    prob_pred = ProblemPredicate(self.alt_domain.get_predicate("U"), [self.alt_problem.get_object(m.name)])
                    model.current_state.add_element(prob_pred)
                elif type(m) == Method:
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

                    occurrences = model.current_state.get_indexes("U")
                    found = False
                    if occurrences is None:
                        occurrences = []
                    for o in occurrences:
                        prob_pred = model.current_state.get_element_index(o)
                        if prob_pred.objects[0].name == task_name:
                            found = True
                            break

                    # If not add name of task this method expands to state
                    if not found:
                        task_name_ob = self.alt_problem.get_object(task_name)
                        if task_name_ob is None:
                            self.alt_problem.add_object(Object(task_name))
                            task_name_ob = self.alt_problem.get_object(task_name)
                        prob_pred = ProblemPredicate(self.alt_domain.get_predicate("U"), [task_name_ob])
                        model.current_state.add_element(prob_pred)
                        # Check if prob_pred in targets
                        task_string = str(prob_pred).replace(" ", "")
                        if task_string in targets:
                            found_targets.append(task_string)
                else:
                    raise TypeError
                # Remove modifiers from list
                applied_modifiers.append(modifiers[modifiers.index(m)])
                del modifiers[modifiers.index(m)]

            # Check exit conditions
            if self._check_targets(targets, found_targets):
                model_store.previous_modifiers = [x for x in applied_modifiers]
                model_store.other_modifiers = [x for x in modifiers]
                return iteration
            elif len(modifiers) == 0 and len(model_store.other_modifiers) > 0 and not used_prev_store:
                modifiers = [x for x in model_store.other_modifiers]
                used_prev_store = True
            elif len(applicable_modifiers) == 0:
                return False

    def _check_targets(self, targets: list, found_targets: list) -> bool:
        if len(targets) == len(found_targets):
            return True
        return False

    def presolving_processing(self) -> None:
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

        # Give alt domain actions
        for a in self.domain.get_all_actions():
            # Consider action with all possible parameters
            param_options = self.parameter_selector.get_potential_parameters(a, {}, None)
            for params in param_options:
                concat_param_names = ""
                for p in params:
                    concat_param_names += "-" + params[p].name
                alt_name = a.name + concat_param_names
                alt_precons = self._process_alt_preconditions(a.get_precondition().get_conditions())
                alt_effects = copy.deepcopy(a.get_effects())
                alt_a = Action(alt_name, a.get_parameters(), alt_precons, alt_effects)
                self.alt_domain.add_action(alt_a)

        # Give alt domain methods
        for m in self.domain.get_all_methods():
            # Consider action with all possible parameters
            param_options = self.parameter_selector.get_potential_parameters(m, {}, None)
            for params in param_options:
                concat_param_names = ""
                for p in params:
                    concat_param_names += "-" + params[p].name
                alt_name = m.name + concat_param_names
                m_precond = m.get_precondition()
                if m_precond is not None:
                    alt_precons = self._process_alt_preconditions(m_precond.get_conditions())
                else:
                    alt_precons = None

                subTs = m.subtasks
                if subTs is not None:
                    alt_subtasks = Subtasks(subTs.ordered)
                    for s in m.subtasks.tasks:
                        alt_subtasks.add_subtask(None, s.task, [x for x in s.parameters])
                else:
                    alt_subtasks = None

                if alt_precons is None:
                    alt_precons = AltPrecondition("Alternate Preconditions Unknown")
                    alt_precons.add_operator_condition("and", None)
                head = alt_precons.head
                if not(type(head) == AltOperatorCondition and head.operator == "and" or head is None):
                    new_op_con = AltOperatorCondition("and", None)
                    old_head = alt_precons.head
                    alt_precons.head = new_op_con
                    head = alt_precons.head

                    if type(old_head) == AltPredicateCondition:
                        alt_precons.add_predicate_condition(old_head.pred, old_head.parameter_name, alt_precons.head)
                    elif type(old_head) == AltOperatorCondition:
                        oh = alt_precons.add_operator_condition(old_head.operator, old_head.parent, old_head.pred)
                        for c in old_head.children:
                            oh.add_child(c)
                    else:
                        raise TypeError("Unsupported type {}".format(type(old_head)))

                if alt_subtasks is not None:
                    for s in alt_subtasks.tasks:
                        alt_subt_name = copy.deepcopy(s.task.name)
                        for p in s.parameters:
                            alt_subt_name += "-" + params[p.name].name
                        alt_precons.add_predicate_condition(self.alt_domain.get_predicate("U"), [alt_subt_name], head)

                alt_m = Method(alt_name, m.get_parameters(), alt_precons, m.get_task_dict(), alt_subtasks, m.get_constraints())
                self.alt_domain.methods[alt_m.name] = alt_m

    def _process_alt_preconditions(self, params, mod=None):
        def __parse_conditions(parameters, parent=None):
            if type(parameters) == list and len(parameters) == 1 and type(parameters[0]) == list:
                parameters = parameters[0]

            if type(parameters) == list:
                i = 0
                l = len(parameters)
                while i < l:
                    p = parameters[i]
                    if type(p) == str:
                        if p == "and" or p == "or" or p == "not":
                            if p == "not":
                                pred_name = parameters[i + 1][0]
                                if pred_name == "=":
                                    cons = constraints.add_operator_condition(p, parent)
                                    __parse_conditions(parameters[i + 1], cons)
                                    return
                                pred_name = "not_" + pred_name
                                pred = self.alt_domain.get_predicate(pred_name)
                                if pred is None:
                                    raise NameError("Predicate '{}' not found in alt_domain".format(pred_name))
                            else:
                                pred = None
                            cons = constraints.add_operator_condition(p, parent, pred)
                            __parse_conditions(parameters[i + 1:], cons)
                            return
                        elif p == "=":
                            cons = constraints.add_operator_condition(p, parent)
                            for v in parameters[i + 1:]:
                                __parse_conditions(v, cons)
                            return
                        elif len(parameters) > 1 and all([type(x) == str for x in parameters]):
                            # Here a type is given
                            # ['valuableorhazardous', '?collect_fees_instance_2_argument_0']
                            pred = self.domain.get_predicate(p)
                            if pred is None:
                                self.domain.add_predicate(Predicate(p, self._parse_parameters(parameters[1:])))
                                pred = self.domain.get_predicate(p)

                            pred_parameters = parameters[1:]
                            """Check if all of the parameters defined in pred_parameters are given from the task
                            (assuming we are parsing a methods precondition)"""
                            if given_params is None:
                                constraints.add_predicate_condition(pred, pred_parameters, parent)
                            else:
                                # Check if all predicate_params are in given_params
                                if all([x in given_params for x in pred_parameters]):
                                    if parent.operator == "not":
                                        parent.parent.children.remove(parent)
                                        operator_parent = constraints.add_given_params_operator_condition("not")
                                        constraints.add_given_params_predicate_condition(pred, pred_parameters,
                                                                                         operator_parent)
                                        parent = parent.parent
                                    else:
                                        constraints.add_given_params_predicate_condition(pred, pred_parameters, parent)
                                else:
                                    constraints.add_predicate_condition(pred, pred_parameters, parent)
                            i = l
                        elif len(parameters) == 1 and type(p) == str:
                            constraints.add_predicate_condition(self.domain.get_predicate(p), [], parent)
                            i = l
                        elif p == "forall":
                            if len(parameters) == 3:
                                selector = parameters[1]
                                satisfier = self._parse_precondition(parameters[2])
                            else:
                                selector = parameters[1] + [self._parse_precondition(['and'] + parameters[2])]
                                satisfier = self._parse_precondition(['and'] + parameters[3])
                            constraints.add_forall_condition(selector, satisfier.head, parent)
                            i += l
                        else:
                            raise TypeError("Unexpected token {}".format(p))
                    elif type(p) == list:
                        __parse_conditions(p, parent)
                    else:
                        raise TypeError("Unexpected type {}".format(type(p)))
                    i += 1
            elif type(parameters) == str:
                return constraints.add_variable_condition(parameters, parent)
            else:
                raise TypeError("Unexpected type {}".format(type(parameters)))

        constraints = AltPrecondition(params)
        if type(mod) == Method:
            given_params = [x.name for x in mod.task['params']]
        else:
            given_params = None
        given_mod = mod
        __parse_conditions(params)
        return constraints

    def _generate_alt_problem(self):
        self.alt_problem.initial_state = State.reproduce(self.problem.initial_state)

        # Get objects
        obs = self.problem.get_all_objects()
        for o in obs:
            self.alt_problem.add_object(obs[o])

        # Create objects for modifiers
        for a in self.alt_domain.actions:
            self.alt_problem.add_object(Object(a))

        for m in self.alt_domain.methods:
            self.alt_problem.add_object(Object(m))

        tasks = self.domain.get_all_tasks()
        for t in tasks:
            # Get all possible combinations of parameter for t
            param_options = self.parameter_selector.get_potential_parameters(tasks[t], {}, None)
            for params in param_options:
                concat_param_names = ""
                for p in params:
                    concat_param_names += "-" + params[p].name
                alt_name = t + concat_param_names
                self.alt_problem.add_object(Object(alt_name))
