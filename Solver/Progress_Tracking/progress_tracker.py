from abc import ABC, abstractmethod
from Internal_Representation.action import Action
from Solver.Progress_Tracking.action_tracker import ActionTracker


class ProgressTracker:
    def __init__(self):
        self.actions_taken = []
        self.operations_taken = []

    @abstractmethod
    def add_operation(self, operation: ActionTracker):
        assert type(operation) == ActionTracker
        if type(operation.mod) == Action:
            self.actions_taken.append(operation)
        self.operations_taken.append(operation)

    @abstractmethod
    def get_num_operations_taken(self):
        return len(self.operations_taken)

    @abstractmethod
    def reproduce(self):
        new_tracker = ProgressTracker()
        for op in self.operations_taken:
            new_tracker.add_operation(op)
        return new_tracker

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if len(self.actions_taken) != len(other.actions_taken):
            return False
        if len(self.operations_taken) != len(other.operations_taken):
            return False
        for i, ac in enumerate(self.actions_taken):
            if other.actions_taken[i] != ac:
                return False
        for i, op in enumerate(self.operations_taken):
            if other.operations_taken[i] != op:
                return False
        return True

    def __str__(self):
        return_str = "\nActions Taken:"
        for a in self.actions_taken:
            return_str += "\n{}".format(a)
        if len(self.actions_taken) == 0:
            return_str += "\nNo Actions"

        return_str += "\n\nOperations Taken:"
        for a in self.operations_taken:
            return_str += "\n{}".format(a)

        return return_str
