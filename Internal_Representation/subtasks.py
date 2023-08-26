import copy
from Internal_Representation.modifier import Modifier
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.Object import Object
from Internal_Representation.list_parameter import ListParameter
from Internal_Representation.parameter import Parameter


class Subtask:
    def __init__(self, task, parameters=[], **kwargs):
        assert isinstance(task, Modifier) or type(task) == str
        self.task = task

        if not ('reproduce' in kwargs and kwargs['reproduce']):
            # If we are not reproducing an existing subtask we need to verify all the parameters beting passed
            assert type(parameters) == list or type(parameters) == ListParameter
            if type(parameters) == list:
                for p in parameters:
                    assert isinstance(p, Parameter)

        self.parameters = parameters
        self.given_params = {}
        self.root_task = False

    def get_name(self) -> str:
        return self.task.name

    def add_given_parameters(self, params: dict):
        assert type(params) == dict
        if not (len(params.keys()) == 1 and type(params[list(params.keys())[0]]) == ListParameter):
            for i in params:
                if not (type(params[i]) == Object or type(params[i]) == ListParameter):
                    raise TypeError('Expected Type Object or ListParameter. But Received: {} of Value {}'.format(type(params[i]), params[i]))
        self.given_params = params

    def evaluate_preconditions(self, model, params, problem) -> bool:
        if self.task.preconditions is None:
            return True
        else:
            return self.task.preconditions.evaluate(params, model, problem)

    def set_root_task(self, v: bool):
        self.root_task = v

    def reproduce(self):
        new_subtask = Subtask(self.task, [*self.parameters], reproduce=True)
        new_subtask.given_params = {}
        for g in self.given_params:
            new_subtask.given_params[g] = self.given_params[g]
        new_subtask.root_task = self.root_task
        return new_subtask

    def __hash__(self):
        given_params_values = tuple(self.given_params.values())
        return hash((self.task.name, given_params_values))

    def __str__(self):
        return_str = self.task.name
        if len(self.given_params) == len(self.parameters):
            for p in self.task.parameters:
                return_str += "-{}".format(self.given_params[p.name].name)
        elif all([type(p) == Object for p in self.parameters]):
            for o in self.parameters:
                return_str += "-{}".format(o.name)
        else:
            raise NotImplementedError
        return return_str

    def __repr__(self):
        return str(self)


class Subtasks:

    def __init__(self, ordered: bool):
        self.tasks = []
        self.labelled_tasks = {}
        self.task_orderings = []
        self.ordered = ordered
        if self.ordered:
            self.task_orderings.append([])

    def add_subtask(self, label: str, modifier: Modifier, parameters: list) -> Subtask:
        assert type(label) == str or label is None
        assert isinstance(modifier, Modifier) or type(modifier) == str
        assert type(parameters) == list or type(parameters) == ListParameter
        if type(parameters) == list:
            for p in parameters:
                assert isinstance(p, Parameter)

        subtask_to_add = Subtask(modifier, parameters)
        if label is not None:
            self.labelled_tasks[label] = subtask_to_add
        self.tasks.append(subtask_to_add)

        if self.ordered:
            self.task_orderings[0].append(subtask_to_add)

        return subtask_to_add

    def order_subtasks(self, orderings):
        # Create orderings
        orderings = self._create_orderings(orderings)

        # Sub in tasks instead of task labels
        orderings = self._sub_tasks_for_labels(orderings)
        self.task_orderings = orderings
        self.ordered = True

    def _create_orderings(self, orderings):
        assert not self.ordered
        """
        Kahns algorithm
        L <- Empty list that will contain the sorted elements
        S <- Set of all nodes with no incoming edge
        
        while S is not empty do
            remove a node n from S
            add n to L
            for each node m with an edge e from n to m do
                remove edge e from the graph
                if m has no other incoming edges then
                    insert m into S
        
        if graph has edges then
            return error   (graph has at least one cycle)
        else 
            return L   (a topologically sorted order)
        """
        class TaskNode:
            def __init__(self, name: str):
                self.name = name
                self.predecessors = []

            def add_predecessor(self, node):
                self.predecessors.append(node)

            def __str__(self):
                return self.name

        task_nodes = {}
        for i in orderings:
            if type(i) != list:
                continue
            symbol = i[0]
            if symbol == "<":
                pred = i[1]
                succ = i[2]
            else:
                pred = i[2]
                succ = i[1]

            if pred not in task_nodes:
                task_nodes[pred] = TaskNode(pred)
            if succ not in task_nodes:
                task_nodes[succ] = TaskNode(succ)

            task_nodes[succ].add_predecessor(task_nodes[pred])

        def kahns_algo(S, ordering=[]):
            if len(S) == 1:
                ordering.append(S[0])
                S = []
                for t in task_nodes:
                    t = task_nodes[t]
                    if t in ordering:
                        continue
                    no_pred = True
                    for p in t.predecessors:
                        if p not in ordering:
                            no_pred = False
                            break
                    if no_pred:
                        S.append(t)
                return kahns_algo(S, ordering)
            elif len(S) == 0:
                return ordering
            else:
                return_orderings = []
                for i in S:
                    res = kahns_algo([i], self.reproduce_list(ordering))
                    if all([type(x) == TaskNode for x in res]):
                        return_orderings.append(res)
                    else:
                        for r in res:
                            return_orderings.append(r)
                return return_orderings

        S = []
        # Populate S
        if orderings == []:
            # Create labels
            count = 0
            for i in self.tasks:
                self.labelled_tasks["task" + str(count)] = i
                # Add to S
                task_nodes["task" + str(count)] = TaskNode("task" + str(count))
                S.append(task_nodes["task" + str(count)])
                count += 1
        else:
            for t in task_nodes:
                t = task_nodes[t]
                if len(t.predecessors) == 0:
                    S.append(t)

        # Kahns Algorithm
        orderings = kahns_algo(S)
        if all([type(x) != list for x in orderings]):
            orderings = [orderings]
        return orderings

    def _sub_tasks_for_labels(self, orderings):
        return_orderings = []
        for o in orderings:
            r_o = []
            for label in o:
                if type(label) != Subtask:
                    r_o.append(self.labelled_tasks[label.name])
                else:
                    r_o.append(label)
            return_orderings.append(r_o)
        return return_orderings

    def get_tasks(self):
        return self.tasks

    def get_task_orderings(self):
        return self.task_orderings

    @staticmethod
    def reproduce_list(l: list):
        l2 = []
        for i in l:
            l2.append(i)
        return l2

    def reproduce(self):
        new_subtasks = Subtasks(self.ordered)
        new_subtasks.tasks = [t.reproduce() for t in self.tasks]
        new_subtasks.labelled_tasks = {}
        for t in self.labelled_tasks:
            new_subtasks.labelled_tasks[t] = new_subtasks.tasks[self.tasks.index(self.labelled_tasks[t])]
        new_subtasks.task_orderings = [*self.task_orderings]
        return new_subtasks

    def __len__(self):
        return len(self.tasks)

    def __str__(self):
        return_str = ""
        for i in self.tasks:
            return_str += str(i)
        return return_str
