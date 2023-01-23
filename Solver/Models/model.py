from abc import ABC, abstractmethod
from Internal_Representation.method import Method
from Internal_Representation.action import Action
from Internal_Representation.task import Task
from Internal_Representation.state import State
from Internal_Representation.subtasks import Subtasks, Subtask
from Solver.Progress_Tracking.progress_tracker import ProgressTracker
from Solver.Progress_Tracking.action_tracker import ActionTracker


class Model(ABC):
    model_counter = 0
    PROGRESS_TRACKER = None

    def __init__(self, state: State, search_modifiers: list, problem=None,
                 waiting_subtasks: list = [], **kwargs):
        assert type(state) == State
        self.current_state = state
        assert type(search_modifiers) == list
        # for m in search_modifiers:
        #     assert type(m) == Subtasks.Subtask and (
        #                 type(m.task) == Method or type(m.task) == Action or type(m.task) == Task)
        self.search_modifiers = search_modifiers
        self.problem = problem  # Problem object from internal rep
        self.waiting_subtasks = waiting_subtasks

        if 'progress_tracker_class' in kwargs:
            assert issubclass(kwargs['progress_tracker_class'], ProgressTracker)
            Model.PROGRESS_TRACKER = kwargs['progress_tracker_class']

        self.progress_tracker = Model.PROGRESS_TRACKER()

        if 'initial_model' in kwargs and kwargs['initial_model']:
            # Mark all tasks as roots
            for sub in self.search_modifiers:
                sub.set_root_task(True)
            for sub in self.waiting_subtasks:
                sub.set_root_task(True)

        self.ranking = None
        self.queue_location = None
        self.num_models_used = None
        self.model_number = self.model_counter
        Model.model_counter += 1
        self.parent_model_number = None

        if "parent_num" in kwargs:
            if type(kwargs['parent_num']) == int:
                self.parent_model_number = kwargs['parent_num']

    def get_model_number(self) -> int:
        return self.model_number

    def set_parent_model_number(self, num: int):
        self.parent_model_number = num

    def set_ranking(self, ranking):
        assert type(ranking) == float or type(ranking) == int
        self.ranking = ranking

    def get_ranking(self):
        return self.ranking

    def set_queue_location(self, queue_locaiton):
        self.queue_location = queue_locaiton

    def set_progress_tracker(self, pt):
        self.progress_tracker = pt

    def get_progress_tracker(self):
        return self.progress_tracker

    def get_num_operations_taken(self):
        return self.progress_tracker.get_num_operations_taken()

    def get_state(self) -> State:
        return self.current_state

    def get_task_network(self):
        return self.search_modifiers + self.waiting_subtasks

    @abstractmethod
    def insert_modifier(self, modifier, index=0):
        raise NotImplementedError

    @abstractmethod
    def get_next_modifier(self) -> Subtask:
        raise NotImplementedError

    @abstractmethod
    def add_operation(self, mod, parameters_used, root=False):
        raise NotImplementedError

    @abstractmethod
    def promote_waiting_subtask(self):
        raise NotImplementedError

    @abstractmethod
    def get_search_modifier(self, index: int) -> Subtask:
        raise NotImplementedError

    @abstractmethod
    def reproduce(self, problem, search_mods=None):
        raise NotImplementedError

    @abstractmethod
    def get_names_of_task_network_modifiers(self):
        raise NotImplementedError

    @staticmethod
    def merge_dictionaries(a, b):
        c = a.copy()
        c.update(b)
        return c

    def __repr__(self):
        return "Model(" + str((self.ranking, self.model_number)) + ")"

    def __lt__(self, other):
        return (self.ranking, self.queue_location) < (other.ranking, other.queue_location)

