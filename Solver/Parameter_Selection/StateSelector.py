from Solver.Models.default_model import DefaultModel
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector


class StateSelector(ParameterSelector):
    def __init__(self, solver):
        super().__init__(solver)

    def get_potential_parameters(self, modifier, parameters: dict, search_model: DefaultModel) -> list:
        modifier_parameters = modifier.parameters
        if len(parameters.keys()) == len(modifier_parameters):
            return self._convert_parameter_options_execution_ready(parameters, len(parameters.keys()))

        modifier_preconditions = modifier.preconditions.conditions
        res = self._select_objects_for_conditions(modifier_preconditions, search_model, parameters, modifier_parameters)
        for p in res:
            res[p] = list(res[p])

        self._check_all_parameters_selected(modifier_parameters, res, parameters)

        converted_list = self._convert_parameter_options_execution_ready(res, len(modifier.parameters))

        return_list = []
        for param_option in converted_list:
            # Check preconditions of new_model
            result = None
            for k in modifier.parameters:
                if not k.name in param_option:
                    result = False

            if result is None:
                result = modifier.evaluate_preconditions(search_model, param_option, self.solver.problem)

            if result:
                return_list.append(param_option)

        return return_list

    def _select_objects_for_conditions(self, conditions, search_model, selected_parameters, all_parameters, param_dict=None, flag=None):
        if param_dict is None:
            param_dict = {}
        not_conditions = []
        for condition in conditions:
            if condition == "and":
                pass
            elif type(condition) == list and condition[0] == 'not':
                not_conditions.append(condition[1:])
            elif type(condition) == list:
                if len(condition) > 1:
                    self._select_objects_satisfy_condition(condition, param_dict, selected_parameters, all_parameters, search_model, flag)
                else:
                    raise NotImplementedError

        for condition in not_conditions:
            self._select_objects_for_conditions(condition, search_model, selected_parameters, all_parameters, param_dict, 'NOT')
        return param_dict

    def _select_objects_satisfy_condition(self, condition, param_dict, selected_parameters, all_parameters, search_model, flag):
        pred_name = condition[0]
        fact_indexes = search_model.current_state.get_indexes(pred_name)
        for i in fact_indexes:
            fact = search_model.current_state.get_element_index(i)
            for p in range(len(condition) - 1):
                param_name = condition[p + 1]

                if param_name in selected_parameters:
                    continue

                if flag is None:
                    if param_name not in param_dict:
                        param_dict[param_name] = set()
                    try:
                        param_dict[param_name].add(fact.objects[p])
                    except Exception as e:
                        raise NotImplementedError
                elif flag == 'NOT':
                    if param_name not in param_dict:
                        req_type = all_parameters[param_name].type
                        param_dict[param_name] = set(self.solver.problem.get_objects_of_type(req_type))
                    param_dict[param_name].remove(fact.objects[p])
                else:
                    raise ValueError("Unknown Flag: {}".format(flag))

    def _check_all_parameters_selected(self, modifier_parameters, param_dict, selected_parameters):
        if len(modifier_parameters) == len(param_dict.keys()):
            return

        for p in modifier_parameters:
            if p.name not in param_dict:
                if p.name not in selected_parameters:
                    param_dict[p.name] = self.solver.problem.get_objects_of_type(p.type)
                else:
                    param_dict[p.name] = selected_parameters[p.name]
                if len(modifier_parameters) == len(param_dict.keys()):
                    return
