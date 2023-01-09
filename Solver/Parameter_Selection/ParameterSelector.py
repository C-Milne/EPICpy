from __future__ import annotations
import sys
from abc import ABC, abstractmethod
"""Import already imported modules from sys.modules"""
from Solver.Models.default_model import DefaultModel
# Model = sys.modules["Solver.model"].Model
# Method = sys.modules["Solver.model"].Method
# Action = sys.modules["Solver.model"].Action
# Task = sys.modules["Solver.model"].Task
Object = sys.modules["Internal_Representation.Object"].Object
ListParameter = sys.modules["Internal_Representation.list_parameter"].ListParameter
Type = sys.modules["Internal_Representation.Type"].Type


class ParameterSelector(ABC):
    def __init__(self, solver):
        self.solver = solver

    @abstractmethod
    def get_potential_parameters(self, modifier, parameters: dict, search_model: DefaultModel) -> list:
        """
        :param modifier: Task / Method / Action that is being executed
        :param parameters: The parameters that are already selected - {'param1': Object ...}
        :param search_model: Search model being expanded
        :return: list of dictionaries containing options of parameters - [{'param1': Object, 'param2': Object ...}, ...]
        """
        raise NotImplementedError

    def presolving_processing(self, domain, problem):
        pass

    def compare_parameters(self, method, parameters: dict) -> list:
        """ Compares if all the parameters required for a method are given
        :parameter  - method : Method
        :parameter  - parameters : {'?objective1': Object, '?mode': Object}
        :returns    - [True] : if parameters match what is required by method
        :returns    - [False, missing_params] : otherwise. missing_params = ["name1", "name2" ... ]
        """
        assert isinstance(method, sys.modules['Internal_Representation.modifier'].Modifier)
        assert type(parameters) == dict
        for p in parameters:
            assert type(parameters[p]) == Object or type(parameters[p]) == ListParameter

        missing_params = []
        for p in method.parameters:
            # Check if a parameter corresponding to p is in parameters dictionary
            if not p.name in parameters:
                missing_params.append(p.name)
                continue
            if not self.check_satisfies_type(p.type, parameters[p.name]):
                return [False, False]
        if len(missing_params) == 0:
            return [True]
        return [False, missing_params]

    def check_satisfies_type(self, required_type: Type, object_to_check: Object) -> bool:
        def __check_type(req_t, t) -> bool:
            if t == req_t:
                return True
            for i in t.parents:
                if __check_type(req_t, i):
                    return True
            return False

        if required_type is None:
            return True
        ob_t = object_to_check.type
        res = __check_type(required_type, ob_t)
        return res

    def _convert_parameter_options_execution_ready(self, param_dict, num_params):
        """The aim of this method is to return a list with all possible combinations of values from param_dict.
        This method is called from self.__find_satisfying_parameters()
        :parameter param_dict: {'?objective': Object, '?mode': Object, '?camera': [Object], '?rover': [Object],
        '?waypoint': [Object, Object, Object, Object]}
        :return: list of dictionaries containing all possible combinations
        """
        combinations = []

        def __create_combinations(remaining_params, selected_params={}):
            if remaining_params == {}:
                combinations.append(selected_params)
                return
            k = list(remaining_params.keys())[0]
            popped = remaining_params.pop(k)
            for po in popped:
                __create_combinations(self.solver.reproduce_dict(remaining_params), DefaultModel.merge_dictionaries(selected_params, {k: po}))

        # Check input format
        for p in param_dict:
            q = param_dict[p]
            if type(q) == Object:
                param_dict[p] = [q]
            elif type(q) == list:
                for i in q:
                    assert type(i) == Object
            else:
                raise TypeError("Unknown type {}".format(type(q)))
        # Create combinations
        __create_combinations(self.solver.reproduce_dict(param_dict))
        return_list = []
        for i in combinations:
            if len(i) == num_params:
                return_list.append(i)
        return return_list
