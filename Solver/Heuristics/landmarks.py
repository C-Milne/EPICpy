from Internal_Representation.task import Task
from Internal_Representation.method import Method
from Internal_Representation.subtasks import Subtask
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Parameter_Selection.All_Parameters import AllParameters


class Node:
    def __init__(self, name):
        self.name = name
        self.requires = []
        self.provides = []

    def add_to_requires(self, task_node):
        self.requires.append(task_node)


class AndNode(Node):
    def __init__(self, name):
        super().__init__(name)


class OrNode(Node):
    def __init__(self, name):
        super().__init__(name)


class AndOrTree:
    def __init__(self):
        self.root = None
        self.nodes = {}

    def add_root_node(self, root_node):
        self.root = root_node

    def get_node(self, node_name, node_type: str = None):
        if node_name in self.nodes:
            return self.nodes[node_name]

        if node_type == 'AND':
            new_node = AndNode(node_name)
        elif node_type == "OR":
            new_node = OrNode(node_name)
        else:
            raise ValueError('Unknown node type: {}'.format(node_type))
        self.nodes[node_name] = new_node
        return new_node


class Landmarks(SeenStatesPruning):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.tree = AndOrTree()
        self.allParameters = AllParameters(self.solver)

    def _inner_ranking(self, model):
        raise NotImplementedError

    def presolving_processing(self) -> None:
        root_node = AndNode('LandMarkRootNode')
        self.tree.add_root_node(root_node)
        initial_tasks = self.problem.get_subtasks()
        for i in initial_tasks:
            self._add_to_node(i, root_node)
        raise NotImplementedError

    def _add_to_node(self, task, parent_node):
        # Get / Create a node for the task
        node_name = str(task)
        if type(task.task) == Task:
            node = self.tree.get_node(node_name, 'OR')
        else:
            node = self.tree.get_node(node_name, 'AND')

        # Add new node as a requirement of parent node
        parent_node.add_to_requires(node)

        # Recur
        if type(task.task) == Task:
            # Create new node for each method
            self._expand_task(task, node)
        elif type(task.task) == Method:
            # Create new node for each subtask
            raise NotImplementedError
        else:
            # Task is an action
            raise NotImplementedError
        print('here')   # TODO: Remove this

    def _expand_task(self, task, node):
        for method in task.task.methods:
            parameters = {}
            i = 0
            for k in task.given_params.keys():
                parameters[method.task['params'][i].name] = task.given_params[k]
                i += 1

            param_options = self.allParameters.get_potential_parameters(method, parameters, None)

            for param_option in param_options:
                subT = Subtask(method, method.parameters)
                subT.add_given_parameters(param_option)
                self._add_to_node(subT, node)
