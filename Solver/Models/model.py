from Internal_Representation.method import Method
from Internal_Representation.action import Action
from Internal_Representation.task import Task
from Internal_Representation.state import State
from Internal_Representation.subtasks import Subtasks
from Solver.Progress_Tracking.action_tracker import ActionTracker   # TODO : Remove this
from Solver.Progress_Tracking.progress_tracker import ProgressTracker
from abc import ABC, abstractmethod

"""The idea here is that this class will contain all information regarding the current state of the environment"""


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
            assert type(kwargs['progress_tracker_class']) == type(ProgressTracker)
            Model.PROGRESS_TRACKER = kwargs['progress_tracker_class']

        self.progress_tracker = Model.PROGRESS_TRACKER()

        if 'initial_model' in kwargs and kwargs['initial_model']:
            # Mark all tasks as roots
            for sub in self.search_modifiers:
                sub.set_root_task(True)
            for sub in self.waiting_subtasks:
                sub.set_root_task(True)

        self.ranking = None
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

    def get_next_modifier(self):
        mod = self.search_modifiers.pop(0)
        return mod

    def get_ranking(self):
        return self.ranking

    def insert_modifier(self, modifier, index=0):
        assert type(modifier) == Task or type(modifier) == Method or type(modifier) == Action or \
               (type(modifier) == Subtasks.Subtask and type(modifier.task) == Action) or \
               (type(modifier) == Subtasks.Subtask and type(modifier.task) == Task)
        self.search_modifiers.insert(index, modifier)

    def add_operation(self, mod, parameters_used, root=False):
        assert type(mod) == Action or type(mod) == Task or type(mod) == Method
        op = ActionTracker(mod, parameters_used, root)
        self.progress_tracker.add_operation(op)

    def set_progress_tracker(self, pt):
        self.progress_tracker = pt

    def get_progress_tracker(self):
        return self.progress_tracker

    def get_num_operations_taken(self):
        return self.progress_tracker.get_num_operations_taken()

    def promote_waiting_subtask(self):
        if len(self.search_modifiers) == 0 and len(self.waiting_subtasks) > 0:
            self.search_modifiers.append(self.waiting_subtasks.pop(0))

    def get_search_modifier(self, index: int):
        return self.search_modifiers[index]

    def get_names_of_task_network_modifiers(self):
        return [x.task.name for x in self.search_modifiers]

    def reproduce(self, problem, search_mods=None):
        if search_mods is None:
            new_model = Model(State.reproduce(self.current_state),
                                          self.search_modifiers, problem, [])
        else:
            new_model = Model(State.reproduce(self.current_state),
                                          search_mods, problem, [])

        i = 0
        for i in self.waiting_subtasks:
            new_model.waiting_subtasks.append(i)

        new_model.set_progress_tracker(self.get_progress_tracker().reproduce())
        return new_model

    @staticmethod
    def merge_dictionaries(a, b):
        c = a.copy()
        c.update(b)
        return c
