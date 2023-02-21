import sys
from Internal_Representation.conditions import Condition, PredicateCondition, OperatorCondition, VariableCondition, \
    ForAllCondition, GoalPredicateCondition, ConstantObjectCondition
Predicate = sys.modules['Internal_Representation.predicate'].Predicate


class Precondition:
    def __init__(self, conditions: str):
        self.head = None
        self.conditions = conditions
        self.conditions_given_params = None # This is the conditions that only include parameters given by the task (not selected parameters)
        self._num_conditions = 0

    def add_operator_condition(self, operator: str, parent: Condition) -> OperatorCondition:
        assert type(operator) == str
        assert isinstance(parent, Condition) or parent is None

        con = OperatorCondition(operator)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_predicate_condition(self, pred: Predicate, parameter_names: list, parent: Condition) -> PredicateCondition:
        assert isinstance(parent, Condition) or parent is None
        con = PredicateCondition(pred, parameter_names)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_variable_condition(self, parameter_name: str, parent: Condition) -> VariableCondition:
        assert isinstance(parent, Condition) or parent is None
        con = VariableCondition(parameter_name)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_constant_object_condition(self, parameter_name: str, parent: Condition, problem) -> ConstantObjectCondition:
        assert isinstance(parent, Condition) or parent is None
        con = ConstantObjectCondition(parameter_name, problem)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_forall_condition(self, selector, satisfier: Condition, parent) -> ForAllCondition:
        """
        :param selector: ['?b', '-', 'block'] OR ['?z', ['package', '?z'], ['at', '?z', '?x']]
        :param satisfier: ['done', '?b']
        :return:
        """
        if len(selector) == 3 and all([type(x) == str for x in selector]):
            assert len(selector) == 3
            selected_variable = selector[0]
            selected_cons = ("type", selector[2])
        else:
            assert len(selector) == 2
            selected_variable = selector[0]
            selected_cons = selector[1]

        con = ForAllCondition(selected_variable, selected_cons, satisfier)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_goal_predicate_condition(self, pred, parameter_names: list, parent: Condition) -> GoalPredicateCondition:
        assert isinstance(parent, Condition) or parent is None
        con = GoalPredicateCondition(pred, parameter_names)
        self._final_condition_addition_checks(con, parent)
        return con

    def add_given_params_predicate_condition(self, pred, parameter_names, parent=None):
        if self.conditions_given_params is None:
            self.conditions_given_params = Precondition("Conditions from Given Parameters")
            self.conditions_given_params.add_operator_condition("and", None)

        if parent is None:
            parent = self.conditions_given_params.head
        self.conditions_given_params.add_predicate_condition(pred, parameter_names, parent)

    def add_given_params_operator_condition(self, operator: str) -> OperatorCondition:
        assert operator == "not"
        if self.conditions_given_params is None:
            self.conditions_given_params = Precondition("Conditions from Given Parameters")
            self.conditions_given_params.add_operator_condition("and", None)
        return self.conditions_given_params.add_operator_condition(operator, self.conditions_given_params.head)

    def _final_condition_addition_checks(self, con, parent):
        if self.head is None:
            self.head = con
        if parent is not None:
            parent.add_child(con)
        con.parent = parent
        self._num_conditions += 1

    def evaluate_given_params_conditions(self, param_dict, search_model, problem) -> bool:
        if self.conditions_given_params is None:
            return True
        return self.conditions_given_params.evaluate(param_dict, search_model, problem)

    def evaluate(self, param_dict, search_model, problem) -> bool:
        if self.head is None:
            return True

        result = self.head.evaluate(param_dict, search_model, problem)
        if result:
            return self.evaluate_given_params_conditions(param_dict, search_model, problem)
        return result

    def get_conditions(self):
        return self.conditions

    @staticmethod
    def merge_dictionaries(a, b):
        c = a.copy()
        c.update(b)
        return c

    def __len__(self):
        if self.conditions_given_params is not None:
            return len(self.conditions) + self._num_conditions
        return self._num_conditions

    def __eq__(self, other):
        try:
            if self.conditions == other.conditions:
                return True
            return False
        except:
            return False
