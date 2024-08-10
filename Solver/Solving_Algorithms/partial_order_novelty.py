import warnings
from Solver.Solving_Algorithms.partial_order import PartialOrderSolver, Model, \
    Subtask, Action, Effects, ProblemPredicate, ForallCondition, Method
from Internal_Representation.state_novelty import StateNovelty
from Internal_Representation.precondition import Precondition
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning


class PartialOrderNoveltySolver(PartialOrderSolver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)
        self._setup_set_search_queue()
        self._setup_set_heuristic()
        self.max_novelty_level = 1

        self.num_novel_states = 0
        self.num_not_novel_states = 0

        self._seen_methods = set()
        self.num_novel_methods = 0
        self.num_not_novel_methods = 0

    def set_search_queue(self, search_queue):
        if issubclass(search_queue, NoveltyGBFSQueue) or isinstance(search_queue, NoveltyGBFSQueue):
            super().set_search_queue(search_queue)
        else:
            warnings.warn("This solver forces the use of Novelty, as such search queue cannot be selected",
                          RuntimeWarning)

    def _setup_set_heuristic(self):
        self.set_heuristic(SeenStatesPruning)

    def _setup_set_search_queue(self):
        self.set_search_queue(NoveltyGBFSQueue)

    def _create_initial_model(self, initial_state, subtasks, waiting_subtasks, progress_tracker_class):
        new_state = StateNovelty()
        new_state.initialise()
        new_state.set_max_novelty_level(self.max_novelty_level)
        new_state.load_from_default_state(initial_state)
        return self.ModelClass(new_state, subtasks, self.problem, waiting_subtasks,
                               progress_tracker_class=progress_tracker_class, initial_model=True)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        if type(addition.task) == Method:
            self._check_method_novelty(addition)
        self.search_models.novelty_add(model, 0)

    def _check_method_novelty(self, addition):
        novelty = 0
        added_method = hash((addition.task, tuple(addition.given_params.values())))
        initial_size = len(self._seen_methods)
        self._seen_methods.add(added_method)
        if initial_size < len(self._seen_methods):
            novelty = 1

        if novelty > 0:
            self.num_novel_methods += 1
        else:
            self.num_not_novel_methods += 1
        return novelty

    def _add_model_to_search_queue_action(self, model, novelty):
        """Add model to search queue after expanding an action"""
        self.search_models.novelty_add(model, novelty)

    def _action_add_fact_to_state(self, new_predicate, novelty_score, search_model):
        add_novel_score = search_model.current_state.add_element(new_predicate)
        if add_novel_score and add_novel_score > novelty_score:
            novelty_score = add_novel_score
        return novelty_score

    def _expand_action_apply_actions(self, subtask, search_model):
        """
        params:
        :subtask - grounded action to be applied
        :search_model - model for action to be applied to
        returns:
        None
        """
        novelty = 0
        effects = subtask.get_effects()
        if effects is not None:
            added_predicates = []
            for eff in effects:
                if type(eff) == Effects.Effect: # TODO: Change this to isinstance
                    # TODO: This line is very similar to the one from the superclass
                    # TODO: is there a way that we can prevent having an entire new method for a small change
                    novelty = self._expand_action_apply_pred_effect_novelty(eff, subtask, search_model, added_predicates
                                                                            , novelty)
                # elif type(eff) == Effects.ForAllEffect:
                elif isinstance(eff, Effects.ForAllEffect):
                    novelty = self._expand_action_apply_forall_effect_novelty(eff, subtask, search_model, novelty)
                else:
                    raise TypeError('Type \'{}\' is not supported as an effect to apply in this method!'.format(
                        type(eff).__name__))
        return novelty

    def _expand_action_apply_pred_effect_novelty(self, eff, subtask, search_model, added_predicates, novelty):
        param_list = self._expand_action_apply_pred_gen_param_list(eff, subtask)

        if eff.negated:
            self._expand_action_apply_pred_effect_remove(eff, param_list, added_predicates, search_model)
        else:
            # Predicate needs to be added
            new_predicate = ProblemPredicate(eff.predicate, param_list)
            added_predicates.append((eff.predicate.name, [x.name for x in param_list]))
            novelty = self._action_add_fact_to_state(new_predicate, novelty, search_model)
        return novelty

    def _expand_action_apply_forall_effect_novelty(self, eff, subtask, search_model, novelty):
        # Get parameters
        precondition_head = eff.get_precondition().get_head()
        assert isinstance(precondition_head, ForallCondition)
        obs = precondition_head.get_satisfying_objects(subtask.given_params, search_model, self.problem)
        forall_var_name = precondition_head.selected_variable
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
                    novelty = self._action_add_fact_to_state(new_predicate, novelty, search_model)
        return novelty

    def _expand_action(self, subtask: Subtask, search_model: Model):
        if self._expand_action_prechecks(subtask, search_model):

            novelty = self._expand_action_apply_actions(subtask, search_model)
            search_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)

            # Track amount of novel and not novel states
            if novelty > 0:
                self.num_novel_states += 1
            else:
                self.num_not_novel_states += 1

            # Add model to search queue
            self._add_model_to_search_queue_action(search_model, novelty)
