from Solver.Progress_Tracking.progress_tracker import ProgressTracker
from Solver.Progress_Tracking.action_tracker import ActionTracker
from Internal_Representation.action import Action
from Internal_Representation.task import Task


class PandaVerifyFormatTracker(ProgressTracker):
    class DecompositionTracker():
        def __init__(self):
            pass

    def __init__(self):
        super().__init__()
        self.ID_counter = 0

    def add_operation(self, operation: ActionTracker):
        assert type(operation) == ActionTracker
        if type(operation.mod) == Action:
            self.actions_taken.append((self.ID_counter, operation))
        self.operations_taken.append((self.ID_counter, operation))
        self.ID_counter += 1

    def get_num_operations_taken(self):
        return super().get_num_operations_taken()

    def reproduce(self):
        new_tracker = PandaVerifyFormatTracker()
        for op in self.operations_taken:
            new_tracker.add_operation(op[1])
        return new_tracker

    def __eq__(self, other):
        raise NotImplementedError

    def __str__(self):
        returnStrActions = ""
        # Section for actions
        returnStrActions += "==>"
        for ac in self.actions_taken:
            returnStrActions += "\n" + str(ac[0]) + " " + self.__extract_details_from_action_tracker(ac[1])

        # Section for all operations
        # Add root
        # TODO: Implement this root part
        returnStrRoot = "\nroot"

        # Add decompositions
        returnStrDecomp = ""
        i = 0
        while i < len(self.operations_taken):
            id = self.operations_taken[i][0]
            op = self.operations_taken[i][1]
            assert type(op.mod) == Task
            if op.root_task:
                returnStrRoot += " " + str(id)
            returnStrDecomp += "\n" + str(id) + " " + self.__extract_details_from_action_tracker(op)

            i += 1
            method = self.operations_taken[i]
            returnStrDecomp += " -> " + str(method[1].mod)
            for j in range(len(method[1].mod.subtasks)):
                i += 1
                added_subtask = self.operations_taken[i]
                returnStrDecomp += " " + str(added_subtask[0])
            i += 1

        returnStr = returnStrActions + returnStrRoot + returnStrDecomp + "\n<=="
        return returnStr

    def __extract_details_from_action_tracker(self, ac) -> str:
        returnStr = ""
        returnStr += str(ac.mod)
        for p in ac.parameters_used.keys():
            returnStr += " " + str(ac.parameters_used[p])
        return returnStr
