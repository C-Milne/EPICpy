import warnings
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver, DefaultModel, \
    Subtask, Action, Effects, ProblemPredicate, ForallCondition
from Internal_Representation.state_novelty import StateNovelty
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning


class PartialOrderNoveltySolver(PartialOrderSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        super().set_search_queue(NoveltyGBFSQueue)
        self.set_heuristic(SeenStatesPruning)
        self.max_novelty_level = 1
        self.num_novel_states = 0
        self.num_not_novel_states = 0

    def set_search_queue(self, search_queue):
        if issubclass(search_queue, NoveltyGBFSQueue):
            super().set_search_queue(search_queue)
        else:
            warnings.warn("This solver forces the use of Novelty, as such search queue cannot be selected", RuntimeWarning)

    def _create_initial_model(self, initial_state, subtasks, waiting_subtasks, progress_tracker_class):
        new_state = StateNovelty()
        new_state.set_max_novelty_level(self.max_novelty_level)
        new_state.load_from_default_state(initial_state)
        return self.ModelClass(new_state, subtasks, self.problem, waiting_subtasks,
                               progress_tracker_class=progress_tracker_class, initial_model=True)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        self.search_models.novelty_add(model, 0)

    def _expand_action(self, subtask: Subtask, search_model: DefaultModel):
        assert type(subtask) == Subtask and type(subtask.task) == Action

        # Check if all the required parameters are given
        comparison_result = self.parameter_selector.compare_parameters(subtask.task, subtask.given_params) # TODO: An optimisation here that removes the need for this would be good. Check the parameters from parameter selectiors

        if not comparison_result[0] == True:
            # raise ValueError('Invalid Parameters Passed to Action')
            return
        # assert comparison_result[0] == True

        # Check preconditions
        if not subtask.evaluate_preconditions(search_model, subtask.given_params, self.problem):
            return

        novelty = 0
        if not subtask.task.effects is None:
            added_predicates = []
            for eff in subtask.task.effects.effects:

                if type(eff) == Effects.Effect:
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

                        add_novel_score = search_model.current_state.add_element(new_predicate)
                        if add_novel_score and add_novel_score > novelty:
                            novelty = add_novel_score
                elif type(eff) == Effects.ForAllEffect:
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

                                add_novel_score = search_model.current_state.add_element(new_predicate)
                                if add_novel_score and add_novel_score > novelty:
                                    novelty = add_novel_score
                else:
                    raise NotImplementedError

        search_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)
        # Track amount of novel and not novel states
        if novelty > 0:
            self.num_novel_states += 1
        else:
            self.num_not_novel_states += 1

        # Add model to search queue
        self.search_models.novelty_add(search_model, novelty)
