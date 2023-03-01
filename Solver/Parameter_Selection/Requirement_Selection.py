import re
import sys
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
"""Import already imported modules from sys.modules"""
Modifier = sys.modules["Internal_Representation.modifier"].Modifier
Method = sys.modules["Internal_Representation.method"].Method
Action = sys.modules["Internal_Representation.action"].Action
Task = sys.modules["Internal_Representation.task"].Task
Model = sys.modules["Solver.Models.model"].Model
Object = sys.modules["Internal_Representation.Object"].Object
ListParameter = sys.modules["Internal_Representation.list_parameter"].ListParameter
Type = sys.modules["Internal_Representation.Type"].Type
RegParameter = sys.modules['Internal_Representation.reg_parameter'].RegParameter
Precondition = sys.modules['Internal_Representation.precondition'].Precondition


class Requirements:
    def __init__(self, parameters, precons: Precondition):
        self.requirements = {}
        self.__prepare_prelayer = []
        self.parameters = parameters
        self.preconditions = precons

    def prepare_requirements(self) -> dict:
        # TODO: Add support for constantObjectConditions
        for p in self.parameters:
            if type(p) == RegParameter:
                self.requirements[p.name] = {"type": p.type, "predicates": {}, "Object": None}
        if self.preconditions is not None:
            self.__prepare_prelayer = []
            self.__prepare_requirements_precons()
            del self.__prepare_prelayer
        return self.requirements

    def __prepare_requirements_precons(self, predicates=None):
        i = 0
        if predicates is None:
            predicates = self.preconditions.conditions

        pred_name = None
        add_prelayer = False
        while i < len(predicates):
            p = predicates[i]
            if type(p) == list:
                self.__prepare_requirements_precons(p)

            if p == "and" or p == "or" or p == "not" or p == "forall":
                self.__prepare_prelayer.append(p)
                add_prelayer = True

            elif p[0] != "?":
                pred_name = p
            elif len(self.__prepare_prelayer) > 0 and self.__prepare_prelayer[-1] == "forall":
                if type(predicates) == list and predicates[0][0] == "?":
                    # Create new forall clause in requirements
                    if len(predicates) == 3:    # [?a - a]
                        req_name = "forall-{}-".format(predicates[2])
                        num = 1
                        while req_name + str(num) in self.requirements.keys():
                            num += 1
                        self.requirements[req_name + str(num)] = {}
                        i += 3
                    elif len(predicates) == 1:
                        req_name = "forall-{}-".format(predicates[0])
                        num = 1
                        while req_name + str(num) in self.requirements.keys():
                            num += 1
                        self.requirements[req_name + str(num)] = {}
                        i += 3
                    else:
                        raise SyntaxError("Unexpected Token {}".format(predicates))
                else:
                    for k in self.requirements.keys():
                        if k.startswith("forall") and self.requirements[k] == {}:
                            self.requirements[k] = {pred_name: p}
            else:
                if p not in self.requirements:
                    self.requirements[p] = {"type": None, "predicates": {}}

                dict = self.requirements[p]["predicates"]
                for l in self.__prepare_prelayer:
                    if l not in dict.keys():
                        dict[l] = {}
                        dict = dict[l]
                    else:
                        dict = dict[l]
                dict[pred_name] = i
            i += 1

        if add_prelayer:
            self.__prepare_prelayer = self.__prepare_prelayer[:-1]


class RequirementSelection(ParameterSelector):
    def __init__(self, solver):
        super().__init__(solver)

    def get_potential_parameters(self, modifier: Modifier, parameters: dict, search_model: Model) -> list:
        comparison_result = self.compare_parameters(modifier, parameters)

        if not comparison_result[0] and not comparison_result[1]:
            return []
        elif not comparison_result[0]:
            found_params = self._find_satisfying_parameters(search_model, modifier.requirements, parameters)
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

    def _find_satisfying_parameters(self, model: Model, given_requirements: dict, param_dict: dict = {}):
        """Find parameters to satisfy a modifier
        :parameter model:
        :parameter requirements: {'type': Type/None, 'predicates': {}}
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
                required_param_name = required_param_name[inds[0]+1:inds[-1]]

                for i in self.solver.problem.objects:
                    i = self.solver.problem.objects[i]
                    match = self.__check_object_satisfies_parameter(model, i, requirements)
                    if match:
                        if required_param_name not in param_dict.keys():
                            param_dict[required_param_name] = [i]
                        else:
                            param_dict[required_param_name].append(i)
            elif required_param_name in param_dict:
                continue
            else:
                requirements = given_requirements[required_param_name]
                for i in self.solver.problem.objects:
                    i = self.solver.problem.objects[i]
                    match = self.__check_object_satisfies_parameter(model, i, requirements)
                    if match:
                        if required_param_name not in param_dict.keys():
                            param_dict[required_param_name] = [i]
                        else:
                            param_dict[required_param_name].append(i)
        if param_dict == {}:
            return False
        # Convert param_dict into a form which can be used - [[?a, ?b, ?c], [?a, ?b, ?d], ... ]
        return self._convert_parameter_options_execution_ready(param_dict, len(given_requirements.keys()))

    def __check_object_satisfies_parameter(self, model: Model, object: Object, requirements: dict):
        """
        :param model:
        :param object:
        :param requirements: {'type': Type, 'predicates': {'and': {'on_board': 1, 'supports': 1}}
        :return: True - If object satisfies the requirements
        :return: False - Otherwise
        """
        required_type = requirements['type']
        required_predicates = requirements['predicates']

        # Check type
        if not self.check_satisfies_type(required_type, object):
            return False

        # If there is no requirements on predicates then the object satisfies
        if required_predicates is None or len(required_predicates) == 0:
            return True

        # Check if each predicate is satisfied
        for pred in required_predicates:
            if pred == "and" or pred == "not" or pred == "or":
                required_param = required_predicates[pred]
                result = []
                for x in required_param.keys():
                    r = self.__check_object_satisfies_parameter(model, object,
                                                                {'type': None, 'predicates': {x: required_param[x]}})
                    if type(r) == list:
                        result += r
                    else:
                        result.append(r)
                if pred == "and":
                    for i in result:
                        if i is False:
                            return False
                    return True
                elif pred == "not":
                    i = 0
                    while i < len(result):
                        result[i] = not result[i]
                        i += 1
                    return result
                else:
                    # pred == or
                    for i in result:
                        if i is True:
                            return True
                    return False
            else:
                indexes = model.current_state.get_indexes(pred)
                if indexes is None:
                    return False
                for index in indexes:
                    try:
                        if object == model.current_state.elements[index].objects[required_predicates[pred] - 1]:
                            return True
                    except IndexError:
                        continue
                    except:
                        raise TypeError
                return False

    def presolving_processing(self, domain, problem):
        # Define requirements for each method and action
        for m in domain.get_all_methods():
            self._prepare_requirements(m)

        for a in domain.get_all_actions():
            self._prepare_requirements(a)

    def _prepare_requirements(self, mod):
        req = Requirements(mod.parameters, mod.preconditions)
        mod.requirements = req.prepare_requirements()
        self._compare_requirements_parameters(mod)

    def _compare_requirements_parameters(self, mod):
        """Check that all the parameters listed in the requirements are present in the parameters list.
        If any are missing; add them"""
        for p in mod.requirements:
            if p.startswith('forall'):
                continue
            if p not in [x.name for x in mod.parameters]:
                mod.add_parameter(RegParameter(p, mod.requirements[p]['type']))
