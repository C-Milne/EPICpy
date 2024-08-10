import sys
from abc import ABC, abstractmethod
from Internal_Representation.predicate import Predicate
from Internal_Representation.Object import Object


class Condition(ABC):
    def __init__(self):
        self.parent = None

    def set_parent(self, condition):
        self.parent = condition

    @abstractmethod
    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        raise NotImplementedError


class PredicateCondition(Condition):
    def __init__(self, pred: Predicate, parameter_names: list):
        super().__init__()
        assert isinstance(pred, Predicate)
        self.pred = pred
        assert type(parameter_names) == list and all([type(x) == str for x in parameter_names])
        self.parameter_name = parameter_names

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        p_list = []
        for i in self.parameter_name:
            if i in param_dict:
                p_list.append(param_dict[i])
            elif i in problem.objects:
                p_list.append(problem.get_object(i))
            else:
                raise NameError("Unknown parameter value {}".format(i))

        return search_model.current_state.check_if_predicate_value_exists(self.pred, p_list)

    def __eq__(self, other):
        try:
            if self.pred == other.pred and self.parameter_name == other.parameter_name:
                return True
            return False
        except:
            return False


class GoalPredicateCondition(Condition):
    def __init__(self, pred: Predicate, parameter_names: list):
        super().__init__()
        assert type(pred) == Predicate
        self.pred = pred
        assert type(parameter_names) == list and all([type(x) == str for x in parameter_names])
        self.parameter_name = parameter_names

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        """Check if predicate is in goal state"""
        if problem.goal_conditions is None:
            return False
        raise NotImplementedError


class VariableCondition(Condition):
    def __init__(self, variable_name: str):
        super().__init__()
        assert type(variable_name) == str
        self.variable_name = variable_name

    def evaluate(self, param_dict: dict, search_model, problem) -> Object:
        return param_dict[self.variable_name]


class ConstantObjectCondition(Condition):
    """
    :precondition (and
        (= ?person ccrew1)
        (= ?veh backhoe1)
        (= ?loc mendon_pond)
        (= ?vehloc strong)
    )
    In this example ccrew1, blackhoe1 ... are constants in the domain
    """
    def __init__(self, object_name: str, problem):
        super().__init__()
        assert type(object_name) == str
        self.object_name = object_name
        self.object = None
        self.problem = problem

    def evaluate(self, param_dict: dict, search_model, problem) -> Object:
        if not self.object:
            self.object = self.problem.get_object(self.object_name)
        return self.object


class OperatorCondition(Condition):
    def __init__(self, operator: str):
        super().__init__()
        assert operator == "and" or operator == "not" or operator == "or" or operator == "="
        self.operator = operator  # and, not, or, =
        self.children = []

    def add_child(self, condition):
        assert isinstance(condition, Condition)
        self.children.append(condition)

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        children_eval = self._evaluate_children(param_dict, search_model, problem)
        if self.operator == "and":
            return self._evaluate_and(children_eval)
        elif self.operator == "or":
            return self._evaluate_or(children_eval)
        elif self.operator == "not":
            return self._evaluate_not(children_eval, param_dict, search_model, problem)
        elif self.operator == "=":
            return self._evaluate_equal(children_eval)

    def _evaluate_children(self, param_dict, search_model, problem):
        children_eval = []
        if len(self.children) > 0:
            children_eval = [x.evaluate(param_dict, search_model, problem) for x in self.children]
        return children_eval

    def _evaluate_and(self, children_eval):
        for i in children_eval:
            if i != True:
                return False
        return True

    def _evaluate_or(self, children_eval):
        for i in children_eval:
            if i == True:
                return True
        return False

    def _evaluate_not(self, children_eval, param_dict, search_model, problem):
        assert len(children_eval) == 1 and type(children_eval[0]) == bool
        return not children_eval[0]

    def _evaluate_equal(self, children_eval):
        v = children_eval[0]
        for i in children_eval[1:]:
            if v != i:
                return False
        return True


class ForAllCondition(Condition):
    def __init__(self, selected_variable: str, selector, satisfier: Condition):
        super().__init__()
        assert isinstance(satisfier, Condition)
        self.selected_variable = selected_variable
        self.selector = selector
        self.selector_requirements = None
        self.satisfier = satisfier

    def evaluate(self, param_dict: dict, search_model, problem) -> bool:
        obs = self._collect_objects(param_dict, search_model, problem)
        for o in obs:
            res = self.satisfier.evaluate(merge_dictionaries(param_dict, {self.selected_variable: o}), search_model, problem)
            if not res:
                return False
        return True

    def _collect_objects(self, param_dict, search_model, problem) -> list:
        if type(self.selector) == tuple and self.selector[0] == "type":
            return problem.get_objects_of_type(self.selector[1])
        elif isinstance(self.selector, sys.modules['Internal_Representation.precondition'].Precondition):   # TODO: Clean up this import
            obs = problem.get_all_objects()

            if self.selector_requirements is None:
                self.selector_requirements = sys.modules['Solver.Solving_Algorithms.solver'].Requirements([], self.selector)    # TODO: Clean up this import
                self.selector_requirements.prepare_requirements()

            # Check there is only one unknown variable
            req_keys = list(self.selector_requirements.requirements.keys())
            given_keys = list(param_dict.keys())
            i = 0
            while i < len(req_keys):
                if req_keys[i] in given_keys:
                    del req_keys[i]
                else:
                    i += 1
            assert len(req_keys) == 1

            req_var_name = req_keys[0]

            return_list = []
            for k in obs:
                if self.selector.evaluate(merge_dictionaries(param_dict, {req_var_name: obs[k]}), search_model, problem):
                    return_list.append(obs[k])
            return return_list
        else:
            raise NotImplementedError

    def get_satisfying_objects(self, param_dict, search_model, problem):
        """
        params:
            param_dict: {'parameter_name': object ...}
            search_model: Model
            problem: Problem

        returns: [Object ... ] List of objects which satisfy the selection constraints of the forall condition

        """
        return self._collect_objects(param_dict, search_model, problem)


def merge_dictionaries(a, b):
    c = a.copy()
    c.update(b)
    return c
