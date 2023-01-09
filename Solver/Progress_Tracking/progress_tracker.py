from abc import ABC, abstractmethod
from Solver.Progress_Tracking.action_tracker import ActionTracker


class ProgressTracker(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def add_operation(self, operation: ActionTracker):
        raise NotImplementedError

    @abstractmethod
    def get_num_operations_taken(self):
        raise NotImplementedError

    @abstractmethod
    def reproduce(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
