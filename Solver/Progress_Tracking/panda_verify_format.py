from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker
from Solver.Progress_Tracking.action_tracker import ActionTracker
from Internal_Representation.action import Action
from Internal_Representation.task import Task


class DecompositionTracker:
    def __init__(self, task, parameters_used, id, root):
        self.task = task
        self.task_id = id
        self.parameters_used = parameters_used
        self.method_decomp_task = None
        self.subtasks = []
        self.root_task = root

    def add_subtask(self, v):
        self.subtasks.append(v)

    def add_decomp_method(self, method):
        assert self.method_decomp_task is None
        self.method_decomp_task = method

    def reproduce(self):
        new_decomp_tracker = DecompositionTracker(self.task, self.parameters_used, self.task_id, self.root_task)
        if self.method_decomp_task:
            new_decomp_tracker.add_decomp_method(self.method_decomp_task)
            for v in self.subtasks:
                new_decomp_tracker.add_subtask(v)
        return new_decomp_tracker

    def __str__(self):
        return '{}: {} -> {}'.format(self.task_id, self.task.name, self.method_decomp_task.name)

    def __repr__(self):
        return str(self)


class PandaVerifyFormatTracker(SequentialTracker):

    def __init__(self):
        super().__init__()

    def add_operation(self, operation: ActionTracker):
        raise NotImplementedError

    def add_task(self, task, parameters_used, ID, root):
        self.operations_taken.append(DecompositionTracker(task, parameters_used, ID, root))

    def add_method(self, method):
        self.operations_taken[-1].add_decomp_method(method)

    def add_action(self, action: ActionTracker, id, root=False):
        self.actions_taken.append((id, action, root))
        # self.operations_taken[-1].add_subtask(id)

    def add_subtask_id(self, id):
        self.operations_taken[-1].add_subtask(id)

    def get_num_operations_taken(self):
        return super().get_num_operations_taken()

    def reproduce(self):
        new_tracker = PandaVerifyFormatTracker()
        new_operations_list = []
        for op in self.operations_taken:
            new_operations_list.append(op.reproduce())
            new_tracker.operations_taken = new_operations_list
        new_actions_list = []
        for ac in self.actions_taken:
            new_actions_list.append((ac[0], ActionTracker(ac[1].mod, ac[1].parameters_used, ac[1].root_task), ac[2]))
        new_tracker.actions_taken = new_actions_list
        return new_tracker

    def __eq__(self, other):
        raise NotImplementedError

    def __str__(self):
        # Add root
        returnStrRoot = "\nroot"

        returnStrActions = ""
        # Section for actions
        returnStrActions += "==>"
        for ac in self.actions_taken:
            returnStrActions += "\n" + str(ac[0]) + " " + self.__extract_details_from_action_tracker(ac[1])
            if ac[2]:
                returnStrRoot += " " + str(ac[0])

        # Add decompositions
        returnStrDecomp = ""

        for i in range(len(self.operations_taken)):
            id = self.operations_taken[i].task_id
            op = self.operations_taken[i]

            if type(op.task) != Task:
                i += 1
                continue
            assert type(op.task) == Task

            if op.root_task:
                returnStrRoot += " " + str(id)
            returnStrDecomp += "\n" + str(id) + " " + self.__extract_details_from_action_tracker(op)

            method = op.method_decomp_task
            returnStrDecomp += " -> " + str(method)

            for sub_task in op.subtasks:
                returnStrDecomp += " " + str(sub_task)

        returnStr = returnStrActions + returnStrRoot + returnStrDecomp + "\n<=="
        return returnStr

    def __extract_details_from_action_tracker(self, ac) -> str:
        returnStr = ""
        if type(ac) == DecompositionTracker:
            returnStr += str(ac.task)
        else:
            returnStr += str(ac.mod)
        for p in ac.parameters_used.keys():
            returnStr += " " + str(ac.parameters_used[p])
        return returnStr
