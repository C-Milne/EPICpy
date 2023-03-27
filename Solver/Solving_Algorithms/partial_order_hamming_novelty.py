import warnings
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver, Subtask, Model, Effects
from Solver.Solving_Algorithms.solver import Solver
from Internal_Representation.state_separate_novelty import StateSeparateNovelty
from Solver.Heuristics.hamming_distance_seen_states import HammingDistanceSeenStatesPruning, HammingDistance
from Solver.Search_Queues.Heu_Novelty_GBFS_Queue import HeuNoveltyGBFSQueue


class PartialOrderHammingNoveltySolver(PartialOrderNoveltySolver, Solver):
    def __init__(self, domain, problem):
        super().__init__(domain, problem)

    def _setup_set_heuristic(self):
        self.set_heuristic(HammingDistanceSeenStatesPruning)

    def _setup_set_search_queue(self):
        self.set_search_queue(HeuNoveltyGBFSQueue)

    def set_search_queue(self, search_queue):
        if issubclass(search_queue, HeuNoveltyGBFSQueue):
            Solver.set_search_queue(self, search_queue)
        else:
            warnings.warn("This solver forces the use of Heuristic based Novelty, as such search queue cannot be selected", RuntimeWarning)

    def set_heuristic(self, heuristic):
        if not issubclass(heuristic, HammingDistance):
            warnings.warn("This solver forces the use of Hamming Distance, as such the heuristic has not been changed", RuntimeWarning)
        else:
            super().set_heuristic(heuristic)

    def _create_initial_model(self, initial_state, subtasks, waiting_subtasks, progress_tracker_class):
        new_state = StateSeparateNovelty()
        new_state.initialise()
        new_state.set_max_novelty_level(self.max_novelty_level)
        new_state.load_from_default_state(initial_state)
        return self.ModelClass(new_state, subtasks, self.problem, waiting_subtasks,
                               progress_tracker_class=progress_tracker_class, initial_model=True)

    def _expand_action(self, subtask: Subtask, search_model: Model):
        if self._expand_action_prechecks(subtask, search_model):

            novelty, hamming_score = self._expand_action_apply_actions(subtask, search_model)
            search_model.add_operation(subtask.task, subtask.given_params, root=subtask.root_task)

            # Track amount of novel and not novel states
            if novelty > 0:
                self.num_novel_states += 1
            else:
                self.num_not_novel_states += 1

            # Add model to search queue
            self._add_model_to_search_queue_action_heuristic(search_model, novelty, hamming_score)

    def _add_model_to_search_queue_action_heuristic(self, model, novelty, heuristic_val):
        """Add model to search queue after expanding an action"""
        self.search_models.heu_novelty_add(model, novelty, heuristic_val)

    def _add_model_to_search_queue(self, model, addition):
        """This is where models are added to the queue after expanding an abstract task or method"""
        self.search_models.heu_novelty_add(model, 0, None)

    def _action_add_fact_to_state(self, new_predicate, novelty_score, search_model):
        search_model.current_state.add_element(new_predicate)

    def _expand_action_apply_actions(self, subtask, search_model):
        novelty = 0
        if not subtask.task.effects is None:
            added_predicates = []
            for eff in subtask.task.effects.effects:
                if type(eff) == Effects.Effect:
                    self._expand_action_apply_pred_effect_novelty(eff, subtask, search_model, added_predicates, novelty)
                elif type(eff) == Effects.ForAllEffect:
                    self._expand_action_apply_forall_effect_novelty(eff, subtask, search_model, novelty)
                else:
                    raise NotImplementedError

        # Now we need to get the Hamming Distance Score
        hamming_score = self.search_models.heuristic.ranking(search_model)

        # Now get the novelty score for this hamming score
        novelty = self._get_novelty_score(hamming_score, search_model)
        return novelty, hamming_score

    def _get_novelty_score(self, hamming_score, search_model):
        if type(hamming_score) != int and (hamming_score is None or hamming_score == False):
            return 0     # This model will be pruned
        novelty_score = search_model.current_state.check_novelty_not_checked_facts(hamming_score)
        return novelty_score
