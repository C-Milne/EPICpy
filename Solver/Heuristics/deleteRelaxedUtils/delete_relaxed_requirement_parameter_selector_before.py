import re
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection, Modifier, Model, Method, Action


class DeleteRelaxedRequirementSelection(RequirementSelection):
    def __init__(self, solver, delete_relaxed_module):
        super().__init__(solver)
        self.delete_relaxed_module = delete_relaxed_module

    def delete_relaxed_get_potential_parameters(self, modifier: Modifier, parameters: dict, search_model: Model):
        if type(modifier) == Method:
            return self._delete_relaxed_get_potential_parameters_method(modifier, parameters, search_model)
        else:
            return self.get_potential_parameters(modifier, parameters, search_model)

    def _delete_relaxed_get_potential_parameters_method(self, modifier, parameters, search_model):
        """
        :param modifier: The modifier we are attempting to add to the task network
        :param parameters:
        :param search_model: The Model we are attempting to add the model to
        :return: List of Lists: containing the possible combinations of objects to use as parameters -> [[ob1, ob2 ...] ...]
        """
        comparison_result = self.compare_parameters(modifier, parameters)

        if not comparison_result[0] and not comparison_result[1]:
            return []
        elif not comparison_result[0]:
            found_params = self._delete_relaxed_find_satisfying_parameters_method(search_model, modifier.requirements, modifier,
                                                                                  parameters)
            if found_params is False:
                found_params = []
        else:
            found_params = [parameters]

        return_list = []
        for param_option in found_params:
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

    def _delete_relaxed_find_satisfying_parameters_method(self, model: Model, given_requirements: dict,  method: Method,
                                                          param_dict: dict = {}):
        """Find parameters to satisfy a modifier
        :parameter model:
        :parameter given_requirements: {'type': Type/None, 'predicates': {'and': {'on_board': 1, 'supports': 1}}}
        :parameter param_dict:    : parameters already set - {'?objective': Object, '?mode': Object}
        :return: list of possible combinations of parameters
        """
        assert isinstance(model, Model)
        assert type(given_requirements) == dict
        assert type(param_dict) == dict
        for required_param_name in given_requirements:
            if required_param_name.startswith('forall-'):
                inner = given_requirements[required_param_name]
                k = list(inner.keys())[0]
                inner[k] = 1
                requirements = {'type': None, 'predicates': inner}

                inds = [m.start() for m in re.finditer('-', required_param_name)]
                required_param_name = required_param_name[inds[0] + 1:inds[-1]]

                for i in self.solver.problem.objects:
                    i = self.solver.problem.objects[i]
                    match = self._check_object_satisfies_parameter(model, i, requirements)
                    if match:
                        if required_param_name not in param_dict.keys():
                            param_dict[required_param_name] = [i]
                        else:
                            param_dict[required_param_name].append(i)
            elif required_param_name in param_dict:
                continue
            else:
                requirements = given_requirements[required_param_name]
                possible_objects = self._delete_relaxed_get_objects_method(requirements['type'], method, required_param_name)
                for object in possible_objects:
                    match = self._check_object_satisfies_parameter(model, object, requirements)
                    if match:
                        if required_param_name not in param_dict.keys():
                            param_dict[required_param_name] = [object]
                        else:
                            param_dict[required_param_name].append(object)
        if param_dict == {}:
            return False
        # Convert param_dict into a form which can be used - [[?a, ?b, ?c], [?a, ?b, ?d], ... ]
        return self._convert_parameter_options_execution_ready(param_dict, len(given_requirements.keys()))

    def _delete_relaxed_get_objects_method(self, required_type, method, required_param_name):
        """Find the objects which satisfy a parameter"""
        valid_options = []
        parameter_used_in_subtask = False

        # If the method has no subtasks we cannot find objects from the already used actions
        if method.subtasks:
            for subtask in method.subtasks.tasks:
                if type(subtask.task) == Action:
                    for p_index in range(len(subtask.parameters)):
                        if subtask.parameters[p_index].name == required_param_name:
                            parameter_used_in_subtask = True
                            potential_objects = self.delete_relaxed_module._used_action_configs[subtask.task.name][p_index]
                            type_checked_potential_objects = set()
                            for ob in potential_objects:
                                if self.check_satisfies_type(required_type, ob):
                                    type_checked_potential_objects.add(ob)
                            if len(type_checked_potential_objects) > 0:
                                valid_options.append(type_checked_potential_objects)

        if not parameter_used_in_subtask:
            return self.solver.problem.get_objects_of_type(required_type)

        if len(valid_options) > 0:
            if len(valid_options) == 1:
                valid_options = list(valid_options.pop())
            else:
                valid_options = list(valid_options.pop().intersection(*valid_options))
        return valid_options

    def _check_object_satisfies_parameter_predicate_exists_check_not(self, model, pred, required_predicates, ob):
        # indexes = model.current_state.get_indexes(pred)
        # indexes_inverse = model.current_state.get_indexes('not_' + pred)
        # if indexes_inverse:
        #     for index in indexes_inverse:
        #         if self._compare_object_to_fact(index, required_predicates[pred] - 1, ob, model):
        #             return True
        # if indexes is None:
        #     return True
        # for index in indexes:
        #     if self._compare_object_to_fact(index, required_predicates[pred] - 1, ob, model):
        #         return False
        # return True
        return True