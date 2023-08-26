from Solver.Solving_Algorithms.solver import Solver, Task, Model, Method
from Solver.Solving_Algorithms.solver import State
from Solver.Solving_Algorithms.solver import Subtasks, Subtask
from Solver.Solving_Algorithms.solver import ProblemPredicate
from Solver.Solving_Algorithms.solver import ForallCondition
from Solver.Solving_Algorithms.solver import Action
from Solver.Solving_Algorithms.solver import Effects


class PartialOrderSolver(Solver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _add_model_to_search_queue(self, model, addition):
        """Params:
        model: The model to be added to the queue
        addition: The task or method that has been expanded
        """
        self.search_models.add(model)

    def _expand_task(self, subtask: Subtask, search_model: Model):
        if len(subtask.task.tasks) != 0:
            for new_task in subtask.task.tasks:
                self._expand_task(Subtask(new_task, self.reproduce_parameter_list(subtask.parameters)),
                                  self.reproduce_model(search_model))
        else:
            # For each method, create a new search model
            for method in subtask.task.methods:
                # Check parameters for new_model
                # Is all the required parameters present or do some need to be chosen
                parameters = {}
                i = 0
                for k in subtask.given_params.keys():
                    parameters[method.task['params'][i].name] = subtask.given_params[k]
                    i += 1

                # Check if the given parameters satisfy preconditions that only use the given parameters
                # TODO: Remove this attribute, self.task_expansion_given_param_check - should always be true
                if self.task_expansion_given_param_check and not method.evaluate_preconditions_conditions_given_params(
                        parameters, search_model, self.problem):
                    # Method not compatible with parameters given from task
                    continue

                param_options = self.parameter_selector.get_potential_parameters(method, parameters, search_model)

                for param_option in param_options:
                    subT = Subtask(method, method.parameters)
                    subT.add_given_parameters(param_option)
                    # Create new model and add to search_models
                    new_model = self.reproduce_model(search_model, [subT] + search_model.search_modifiers)
                    new_model.set_parent_model_number(search_model.get_model_number())
                    new_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)
                    self._add_model_to_search_queue(new_model, subtask)

    def _expand_method(self, subtask: Subtask, search_model: Model):
        """
        params:
        :subtask - the method being applied
        :search_model - the model the method is being applied to

        :returns: None

        This function applies a given method to a given model.
        For example the task network of the model would go from : [method, task1, ...]
        To something like : [method_subtask1, method_subtask2, task1, ...]

        All the subtasks added to the task network need to be grounded subtask_index.e. assigned objects as parameters
        """
        method_to_be_applied = subtask.task

        if subtask.task.subtasks is None:
            search_model.add_operation(subtask.task, subtask.given_params)
            self.search_models.add(search_model)
            return

        for subtask_option in subtask.task.subtasks.task_orderings:
            subtask_index = 0  # The index of the subtask being added to the task network
            search_model = self.reproduce_model(search_model)

            for method_subtask in subtask_option:
                if method_subtask.task is None:
                    # TODO: We should not have any subtasks that are empty. Is this check still used??
                    continue
                assert type(method_subtask.task) == Action or type(method_subtask.task) == Task

                method_subtask = Subtask(method_subtask.task, method_subtask.parameters)

                # TODO: Can we re-write this to pass parameters to subtasks without creating new dictionary - pass as a list
                parameters = self._expand_method_check_parameters(method_subtask, subtask)
                method_subtask.add_given_parameters(parameters)

                # Add method_subtask to search_model
                search_model.insert_modifier(method_subtask, subtask_index)
                subtask_index += 1
            search_model.add_operation(subtask.task, subtask.given_params)
            self._add_model_to_search_queue(search_model, subtask)

    def _expand_method_check_parameters(self, method_subtask, subtask):
        # Check parameter count
        parameters = {}

        """
        If we have a method with the parameters: [?from, ?x, ?s]
        And pass the following parameters to a subtask: [?x, ?from]
        And the subtask renames the parameters: [?x, ?to]
        """

        parameter_names_required_from_method = [p.name for p in method_subtask.parameters]
        subtask_parameter_names = [p.name for p in method_subtask.task.parameters]

        if len(subtask_parameter_names) > 0:
            # If we have parameters to pass
            for j in range(len(subtask_parameter_names)):
                try:
                    # TODO: This try block is bad code and needs to be removed and rewritten
                    # TODO: check if the object we need is a constant - this is the keyerror block
                    parameters[subtask_parameter_names[j]] = subtask.given_params[parameter_names_required_from_method[j]]
                except IndexError:
                    # TODO: What is this for?
                    pass
                except KeyError as e:
                    if parameter_names_required_from_method[j][0] != "?" and parameter_names_required_from_method[j] in self.problem.objects:
                        parameters[subtask_parameter_names[j]] = self.problem.get_object(parameter_names_required_from_method[j])
                    else:
                        raise KeyError(e)
        else:
            # No parameters to pass??
            for j in range(len(parameter_names_required_from_method)):
                # TODO: Can we not simply make this a straight assignment?
                parameters[parameter_names_required_from_method[j]] = subtask.given_params[parameter_names_required_from_method[j]]
        return parameters

    def _expand_action_prechecks(self, subtask, search_model):
        assert type(subtask) == Subtask and type(subtask.task) == Action

        # Check if all the required parameters are given
        comparison_result = self.parameter_selector.compare_parameters(subtask.task,
                                                                       subtask.given_params)  # TODO: An optimisation here that removes the need for this would be good. Check the parameters from parameter selectiors

        if not comparison_result[0] == True:
            # raise ValueError('Invalid Parameters Passed to Action')
            return False
        # assert comparison_result[0] == True

        # Check preconditions
        if not subtask.evaluate_preconditions(search_model, subtask.given_params, self.problem):
            return False
        return True

    def _expand_action_apply_actions(self, subtask, search_model):
        if not subtask.task.effects is None:
            added_predicates = []
            for eff in subtask.task.effects.effects:
                if type(eff) == Effects.Effect:
                    self._expand_action_apply_pred_effect(eff, subtask, search_model, added_predicates)
                elif type(eff) == Effects.ForAllEffect:
                    self._expand_action_apply_forall_effect(eff, subtask, search_model)
                else:
                    raise NotImplementedError

    def _expand_action_apply_pred_gen_param_list(self, eff, subtask):
        param_list = []
        for i in eff.parameters:
            if i in subtask.given_params:
                param_list.append(subtask.given_params[i])
            else:
                # Check constants
                const = self.domain.get_constant(i)
                assert const is not None
                param_list.append(const)
        return param_list

    def _expand_action_apply_pred_effect(self, eff, subtask, search_model, added_predicates):
        param_list = self._expand_action_apply_pred_gen_param_list(eff, subtask)

        if eff.negated:
            self._expand_action_apply_pred_effect_remove(eff, param_list, added_predicates, search_model)
        else:
            # Predicate needs to be added
            new_predicate = ProblemPredicate(eff.predicate, param_list)
            added_predicates.append((eff.predicate.name, [x.name for x in param_list]))
            search_model.current_state.add_element(new_predicate)

    def _expand_action_apply_pred_effect_remove(self, eff, param_list, added_predicates, search_model):
        # Predicate needs to be removed
        if (eff.predicate.name, [x.name for x in param_list]) not in added_predicates:
            # If an action tries to add and remove the same predicate we don't delete anything
            search_model.current_state.remove_element(eff.predicate, param_list)

    def _expand_action_apply_forall_effect(self, eff, subtask, search_model):
        # Get parameters
        assert type(eff.precondition.head) == ForallCondition
        obs = eff.precondition.head.get_satisfying_objects(subtask.given_params, search_model, self.problem)
        forall_var_name = eff.precondition.head.selected_variable
        # Iterate over found parameters
        for o in obs:
            for e in eff.effects:
                param_list = []
                for i in e.parameters:
                    if i.name == forall_var_name:
                        param_list.append(o)
                    else:
                        param_list.append(subtask.given_params[i.name])

                if eff.negated:
                    # Predicate needs to be removed
                    search_model.current_state.remove_element(e.predicate, param_list)
                else:
                    # Predicate needs to be added
                    new_predicate = ProblemPredicate(e.predicate, param_list)
                    search_model.current_state.add_element(new_predicate)

    def _expand_action(self, subtask: Subtask, search_model: Model):
        if self._expand_action_prechecks(subtask, search_model):
            self._expand_action_apply_actions(subtask, search_model)
            search_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)
            self.search_models.add(search_model)
