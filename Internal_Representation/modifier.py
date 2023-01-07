import sys
from typing import List
# from Internal_Representation.precondition import Precondition
from Internal_Representation.parameter import Parameter

if 'Internal_Representation.precondition' in sys.modules:
    Precondition = sys.modules['Internal_Representation.precondition'].Precondition
else:
    from Internal_Representation.precondition import Precondition


class Modifier:

    def __init__(self, name, parameters: List[Parameter], preconditions: Precondition = None):
        assert type(name) == str
        self.name = name
        assert type(parameters) == list
        for p in parameters:
            assert isinstance(p, Parameter)
        self.parameters = parameters
        assert isinstance(preconditions, Precondition) or preconditions is None
        self.preconditions = preconditions

    def add_parameter(self, parameter: Parameter):
        assert isinstance(parameter, Parameter)
        self.parameters.append(parameter)

    def get_parameters(self) -> List[Parameter]:
        return self.parameters

    def add_preconditions(self, precons: Precondition):
        assert type(precons) == Precondition or precons is None
        if self.preconditions is None:
            self.preconditions = precons
        else:
            raise TypeError("Preconditions are already set for this modifier")

    def get_number_parameters(self) -> int:
        return len(self.parameters)

    def get_precondition(self):
        return self.preconditions

    def get_name(self):
        if self.name is None:
            return 'Unknown'
        return self.name

    def get_parameter_names(self):
        if len(self.parameters) != len(self.parameter_names):
            self.__collect_parameter_names()
        return self.parameter_names

    def __collect_parameter_names(self):
        self.parameter_names = []
        for p in self.parameters:
            self.parameter_names.append(p.name)

    def evaluate_preconditions(self, model, param_dict, problem) -> bool:
        """:params  - model : proposed model
                    - param_dict : dictionary of parameters
                    - problem : problem being solved
        :returns    - True : if method can be run on the given model with given parameters
                    - False : Otherwise"""
        # Evaluate preconditions
        if self.preconditions is None:
            return True
        assert isinstance(self.preconditions, Precondition)
        return self.preconditions.evaluate(param_dict, model, problem)

    def evaluate_preconditions_conditions_given_params(self, param_dict, search_model, problem) -> bool:
        if self.preconditions is None:
            return True
        # TODO : Add a check for types here - current method checks the types given when executing an action (requirement selector fixes this issue)
        return self.preconditions.evaluate_given_params_conditions(param_dict, search_model, problem)

    def __str__(self):
        return self.name
