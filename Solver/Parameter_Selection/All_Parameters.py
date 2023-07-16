import sys
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
"""Import already imported modules from sys.modules"""
Modifier = sys.modules["Internal_Representation.modifier"].Modifier
Method = sys.modules["Internal_Representation.method"].Method
Action = sys.modules["Internal_Representation.action"].Action
Task = sys.modules["Internal_Representation.task"].Task
Model = sys.modules["Solver.Models.default_model"].DefaultModel
Object = sys.modules["Internal_Representation.Object"].Object
ListParameter = sys.modules["Internal_Representation.list_parameter"].ListParameter
Type = sys.modules["Internal_Representation.Type"].Type


class AllParameters(ParameterSelector):
    def __init__(self, solver):
        super().__init__(solver)

    def get_potential_parameters(self, modifier: Modifier, parameters: dict, search_model: Model) -> list:
        assert isinstance(modifier, Modifier)
        parameters_to_select = [x for x in modifier.parameters if x.name not in parameters]
        parameter_options = self.solver.reproduce_dict(parameters)

        for p in parameters_to_select:
            # For each parameter that needs to be selected
            # Get the required type
            # Get all objects of that type
            if p.name not in parameter_options:
                parameter_options[p.name] = []

            # TODO: Optimise this - store which objects satisfy each type during problem parsing
            if p.type is not None:
                for x in self.solver.problem.objects:
                    x = self.solver.problem.objects[x]
                    if self.check_satisfies_type(p.type, x):
                        parameter_options[p.name].append(x)
            else:
                for x in self.solver.problem.objects:
                    x = self.solver.problem.objects[x]
                    parameter_options[p.name].append(x)

        # Return all combinations
        return self._convert_parameter_options_execution_ready(parameter_options, len(modifier.parameters))
