from Solver.Models.model import Model, State
from Solver.Progress_Tracking.panda_verify_format import PandaVerifyFormatTracker
from Internal_Representation.task import Task
from Internal_Representation.method import Method
from Internal_Representation.action import Action
from Solver.Progress_Tracking.action_tracker import ActionTracker


class PandaVerifyModel(Model):

    class PandaVerifyTaskNetworkNode:
        def __init__(self, subtask, id):
            self.subtask = subtask
            self.ID = id

    def __init__(self, state: State, search_modifiers: list, problem=None,
                 waiting_subtasks: list = [], **kwargs):
        super().__init__(state, search_modifiers, problem, waiting_subtasks, **kwargs)
        self.id_counter = 0
        self.progress_tracker = PandaVerifyFormatTracker()
        if not all([type(x) == self.PandaVerifyTaskNetworkNode for x in self.search_modifiers]):
            i = 0
            while i < len(self.search_modifiers):
                if type(self.search_modifiers[i]) != self.PandaVerifyTaskNetworkNode:
                    self.search_modifiers[i] = self.PandaVerifyTaskNetworkNode(self.search_modifiers[i], self.id_counter)
                    self.id_counter += 1
                i += 1
        self.last_dispense = None

    def insert_modifier(self, modifier, index=0):
        """This method add modifiers to the task network (search_modifiers)"""
        self.search_modifiers.insert(index, self.PandaVerifyTaskNetworkNode(modifier, self.id_counter))

        if type(modifier.task) == Action:
            # We need to add the action to the progress tracker no, or else we wont be able to determine which method added it to the task network
            self.progress_tracker.add_subtask_id(self.id_counter)
        elif type(modifier.task) == Task:
            self.progress_tracker.add_subtask_id(self.id_counter)
        else:
            raise NotImplementedError
        self.id_counter += 1

    def add_operation(self, mod, parameters_used, root=False):
        """This method records which operations have been taken by the planner"""
        if type(mod) == Action:
            self.progress_tracker.add_action(ActionTracker(mod, parameters_used), self.last_dispense.ID)
        elif type(mod) == Method:
            self.progress_tracker.add_method(mod)
        elif type(mod) == Task:
            assert mod == self.last_dispense.subtask.task
            self.progress_tracker.add_task(mod, parameters_used, self.last_dispense.ID, root)
            self.last_dispense = None
        else:
            raise TypeError('Unsure how to handle type {}'.format(type(mod)))

    def get_next_modifier(self):
        next_mod = self.search_modifiers.pop(0)
        self.last_dispense = next_mod
        return next_mod.subtask

    def get_names_of_task_network_modifiers(self):
        return [x.subtask.task.name for x in self.search_modifiers]

    def promote_waiting_subtask(self):
        if len(self.search_modifiers) == 0 and len(self.waiting_subtasks) > 0:
            self.search_modifiers.append(self.PandaVerifyTaskNetworkNode(self.waiting_subtasks.pop(0), self.id_counter))
            self.id_counter += 1

    def get_search_modifier(self, index: int):
        return self.search_modifiers[index].subtask

    def reproduce(self, problem, search_mods=None):
        if search_mods is None:
            new_model = PandaVerifyModel(State.reproduce(self.current_state),
                                          self.search_modifiers, problem, [])
        else:
            new_model = PandaVerifyModel(State.reproduce(self.current_state),
                                          search_mods, problem, [])

        for i in self.waiting_subtasks:
            new_model.waiting_subtasks.append(i)

        new_model.set_progress_tracker(self.get_progress_tracker().reproduce())
        new_model.set_last_dispense(self.last_dispense)
        new_model.set_counter(self.id_counter)
        return new_model

    def set_counter(self, i):
        self.id_counter = i

    def set_last_dispense(self, node: PandaVerifyTaskNetworkNode):
        self.last_dispense = node