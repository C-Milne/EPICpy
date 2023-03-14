from Internal_Representation.method import Method
from Internal_Representation.action import Action
from Internal_Representation.task import Task
from Internal_Representation.state import State
from Internal_Representation.subtasks import Subtask
from Solver.Progress_Tracking.action_tracker import ActionTracker   # TODO : Remove this
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker
from Solver.Models.model import Model

"""The idea here is that this class will contain all information regarding the current state of the environment"""


class DefaultModel(Model):

    def __init__(self, state: State, search_modifiers: list, problem=None, waiting_subtasks: list = [], **kwargs):
        super().__init__(state, search_modifiers, problem, waiting_subtasks, **kwargs)

    def get_next_modifier(self):
        mod = self.search_modifiers.pop(0)
        return mod

    def insert_modifier(self, modifier, index=0):
        assert type(modifier) == Task or type(modifier) == Method or type(modifier) == Action or \
               (type(modifier) == Subtask and type(modifier.task) == Action) or \
               (type(modifier) == Subtask and type(modifier.task) == Task)
        self.search_modifiers.insert(index, modifier)

    def add_operation(self, mod, parameters_used, root=False):
        assert type(mod) == Action or type(mod) == Task or type(mod) == Method
        op = ActionTracker(mod, parameters_used, root)
        self.progress_tracker.add_operation(op)

    def promote_waiting_subtask(self):
        if len(self.search_modifiers) == 0 and len(self.waiting_subtasks) > 0:
            self.search_modifiers.append(self.waiting_subtasks.pop(0))

    def get_search_modifier(self, index: int):
        return self.search_modifiers[index]

    def get_names_of_task_network_modifiers(self):
        return [x.task.name for x in self.search_modifiers]

    def reproduce(self, problem, search_mods=None):
        if search_mods is None:
            new_model = DefaultModel(self.current_state,
                                     self.search_modifiers, problem, [])
        else:
            new_model = DefaultModel(self.current_state,
                                     search_mods, problem, [])

        new_model.waiting_subtasks = [*self.waiting_subtasks]

        new_model.set_progress_tracker(self.get_progress_tracker().reproduce())
        new_model.ranking = self.ranking
        new_model.set_parent_model_number(self.model_number)
        return new_model
