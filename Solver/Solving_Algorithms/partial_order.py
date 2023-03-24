from Solver.Solving_Algorithms.solver import Solver, Task
from Solver.Solving_Algorithms.solver import DefaultModel
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

    def _expand_task(self, subtask: Subtask, search_model: DefaultModel):
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

    def _expand_method(self, subtask: Subtask, search_model: DefaultModel):
        # Add actions to search model - with parameters
        i = 0
        if subtask.task.subtasks is None:
            search_model.add_operation(subtask.task, subtask.given_params)
            self.search_models.add(search_model)
            return

        for subtask_option in subtask.task.subtasks.task_orderings:
            search_mod = self.reproduce_model(search_model)

            for mod in subtask_option:
                if mod.task is None:
                    continue
                assert type(mod.task) == Action or type(mod.task) == Task

                mod = Subtask(mod.task, mod.parameters)

                # Check parameter count
                parameters = {}
                param_keys = [p.name for p in mod.parameters]
                action_keys = [p.name for p in mod.task.parameters]
                if len(action_keys) > 0:
                    for j in range(len(action_keys)):
                        try:
                            parameters[action_keys[j]] = subtask.given_params[param_keys[j]]
                        except IndexError:
                            pass
                        except KeyError as e:
                            if param_keys[j][0] != "?" and param_keys[j] in self.problem.objects:
                                parameters[action_keys[j]] = self.problem.get_object(param_keys[j])
                            else:
                                raise KeyError(e)
                else:
                    for j in range(len(param_keys)):
                        parameters[param_keys[j]] = subtask.given_params[param_keys[j]]

                mod.add_given_parameters(parameters)

                # Add mod to search_model
                search_mod.insert_modifier(mod, i)
                i += 1
            search_mod.add_operation(subtask.task, subtask.given_params)
            self._add_model_to_search_queue(search_mod, subtask)

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

    def _expand_action_apply_pred_effect(self, eff, subtask, search_model, added_predicates):
        param_list = []
        for i in eff.parameters:
            if i in subtask.given_params:
                param_list.append(subtask.given_params[i])
            else:
                # Check constants
                const = self.domain.get_constant(i)
                assert const is not None
                param_list.append(const)

        if eff.negated:
            # Predicate needs to be removed
            if (eff.predicate.name, [x.name for x in param_list]) not in added_predicates:
                # If an action tries to add and remove the same predicate we don't delete anything
                search_model.current_state.remove_element(eff.predicate, param_list)
        else:
            # Predicate needs to be added
            new_predicate = ProblemPredicate(eff.predicate, param_list)
            added_predicates.append((eff.predicate.name, [x.name for x in param_list]))
            search_model.current_state.add_element(new_predicate)

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

    def _expand_action(self, subtask: Subtask, search_model: DefaultModel):
        if self._expand_action_prechecks(subtask, search_model):
            self._expand_action_apply_actions(subtask, search_model)
            search_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)
            self.search_models.add(search_model)
