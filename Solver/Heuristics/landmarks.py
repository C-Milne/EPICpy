import copy
from Internal_Representation.task import Task
from Internal_Representation.method import Method
from Internal_Representation.subtasks import Subtask
from Internal_Representation.state_novelty import StateNovelty
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Parameter_Selection.All_Parameters import AllParameters
# from Solver.Heuristics.delete_relaxed import DeleteRelaxed, ProblemPredicate
from Solver.Heuristics.delete_relaxed_before import DeleteRelaxed, ProblemPredicate


class Node:
    def __init__(self, name):
        self.name = name
        self.requires = []
        self.required_by = []
        self.provides = []
        self.provided_by = []
        self.landmarks_calculated = False
        self.landmarks = set()
        self._already_seen = set()
        self.previous_landmark_calculate_positives = 0
        self.upwards_recur_seen = set()
        self.child_list_hash = None

    def add_to_requires(self, task_node):
        if task_node not in self.requires:
            self.requires.append(task_node)

    def add_to_required_by(self, node):
        # Check that the node is not already in the required by list
        if node not in self.required_by:
            self.required_by.append(node)

    def add_to_provides(self, node):
        if node not in self.provides:
            self.provides.append(node)

    def add_to_provided_by(self, node):
        if node not in self.provided_by:
            self.provided_by.append(node)

    def calculate_landmarks(self):
        raise NotImplementedError

    def add_to_already_seen(self, task_name: str):
        self._already_seen.add(task_name)

    def in_already_seen(self, task_name: str) -> bool:
        return task_name in self._already_seen

    def set_already_seen(self, seen_set):
        self._already_seen = {*seen_set}

    def get_already_seen(self) -> set:
        return self._already_seen

    def get_child_landmark_calculated_num(self):
        raise NotImplementedError

    def hash_child_list(self):
        return hash(frozenset([hash(x) for x in self.required_by]))

    def __hash__(self):
        return hash(frozenset(self.landmarks))

    def __str__(self):
        return self.name


class AndNode(Node):
    def __init__(self, name):
        super().__init__(name)

    def calculate_landmarks(self):
        """The landmarks of an AndNode is the union of its requirements plus itself"""
        # if self.landmarks_calculated:
        #     print('Duplicate Landmark Calculation: {}'.format(self.name))
        # else:
        #     print('Landmark Calculation: {}'.format(self.name))

        if not self.name.startswith('FACT--'):
            assert all([r.landmarks_calculated for r in self.requires])
            self.landmarks = self.landmarks.union(*[s.landmarks for s in self.requires], {self.name})
        else:
            self.landmarks = self.landmarks.union(*[s.landmarks for s in self.provided_by])
        self.landmarks_calculated = True
        self.previous_landmark_calculate_positives = self.get_child_landmark_calculated_num()
        self.child_list_hash = self.hash_child_list()

    def set_landmarks_initial_fact(self):
        assert self.name.startswith('FACT--')
        self.landmarks = {self.name}
        self.landmarks_calculated = True

    def get_child_landmark_calculated_num(self):
        return sum([r.landmarks_calculated for r in self.requires] + [r.landmarks_calculated for r in self.provided_by])


class FactNode(AndNode):
    def __init__(self, name):
        super().__init__(name)

    def get_child_landmark_calculated_num(self):
        return sum([r.landmarks_calculated for r in self.provided_by])


class OrNode(Node):
    def __init__(self, name):
        super().__init__(name)

    def calculate_landmarks(self):
        """The landmarks of an OrNode is the intersection of its requirements, union itself"""
        assert any([r.landmarks_calculated for r in self.requires])
        # if self.landmarks_calculated:
        #     print('Duplicate Landmark Calculation: {}'.format(self.name))
        # else:
        #     print('Landmark Calculation: {}'.format(self.name))

        if len(self.requires) > 1:
            self.landmarks = self.requires[0].landmarks.intersection(*[s.landmarks for s in self.requires[1:] if s.landmarks_calculated])
        elif len(self.requires) > 0:
            self.landmarks = self.requires[0].landmarks
        self.landmarks = self.landmarks.union({self.name})
        self.landmarks_calculated = True
        self.previous_landmark_calculate_positives = self.get_child_landmark_calculated_num()
        self.child_list_hash = self.hash_child_list()

    def get_child_landmark_calculated_num(self):
        return sum([r.landmarks_calculated for r in self.requires])


class LeafNodes:
    def __init__(self, tree):
        self.leaf_nodes = []    # This is the nodes to be calculated
        self.leaf_node_names = set()    # Set of names of nodes in self.leaf_nodes
        self.leaf_nodes_recalc = []     # This is the nodes to be recalculated
        self.leaf_node_recalc_names = set()     # Set of names of nodes in self.leaf_nodes_recalc
        self.tree = tree

    def add_leaf_node(self, node, upwards_recur_seen: set = set(), **kwargs):
        node.upwards_recur_seen = node.upwards_recur_seen.union(upwards_recur_seen)
        if 'priority' in kwargs and kwargs['priority']:
            # Remove the node from both lists
            self.remove_leaf_node(node)
            self.leaf_nodes_recalc.insert(0, node)
            self.leaf_node_recalc_names.add(node.name)
        elif node.name not in self.leaf_node_names and node.name not in self.leaf_node_recalc_names:
            if node.landmarks_calculated:
                self.leaf_nodes_recalc.append(node)
                self.leaf_node_recalc_names.add(node.name)
            else:
                self.leaf_nodes.append(node)
                self.leaf_node_names.add(node.name)

    def pop_leaf_node(self):
        if len(self.leaf_node_names) > 0:
            return_node = self.leaf_nodes.pop()
            self.leaf_node_names.remove(return_node.name)
        else:
            return_node = self.leaf_nodes_recalc.pop()
            self.leaf_node_recalc_names.remove(return_node.name)

        upwards_recur_seen = return_node.upwards_recur_seen
        return_node.upwards_recur_seen = set()
        return return_node, upwards_recur_seen

    def remove_leaf_node(self, node):
        if type(node) == str:
            node = self.tree.get_existing_node(node)
        if node.name in self.leaf_node_names:
            self.leaf_nodes.remove(node)
            self.leaf_node_names.remove(node.name)
        if node.name in self.leaf_node_recalc_names:
            self.leaf_nodes_recalc.remove(node)
            self.leaf_node_recalc_names.remove(node.name)

    def __contains__(self, item):
        if isinstance(item, Node):
            return item.name in self.leaf_node_names
        elif type(item) == str:
            return item in self.leaf_node_names
        else:
            raise TypeError

    def __bool__(self):
        if len(self.leaf_node_names) > 0 or len(self.leaf_node_recalc_names) > 0:
            return True
        return False


class AndOrTree:
    def __init__(self):
        self.root = None
        self.nodes = {}
        self.leaf_nodes = LeafNodes(self)

    def add_root_node(self, root_node):
        self.root = root_node

    def get_node(self, node_name, node_type: str, parent_node):
        if node_name in self.nodes:
            return self.nodes[node_name], True

        if node_type == 'AND':
            new_node = AndNode(node_name)
        elif node_type == "OR":
            new_node = OrNode(node_name)
        elif node_type == "FACT":
            new_node = FactNode(node_name)
        else:
            raise ValueError('Unknown node type: {}'.format(node_type))
        if parent_node is not None:
            new_node.set_already_seen(parent_node.get_already_seen())
        self.nodes[node_name] = new_node
        self.leaf_nodes.add_leaf_node(new_node)
        return new_node, False

    def get_existing_node(self, node_name):
        if node_name in self.nodes:
            return self.nodes[node_name]
        return None

    def get_node_for_ranking(self, node_name):
        return self.nodes[node_name]


class Landmarks(SeenStatesPruning):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.tree = AndOrTree()
        self.reachability = None
        self.method_reachability = None
        self.alt_problem = None
        self.alt_domain = None
        self.allParameters = AllParameters(self.solver)

    def _inner_ranking(self, model):
        missing_landmarks = 0
        for l in self.tree.root.landmarks:
            if l.startswith('FACT--'):
                # TODO: Implement this
                raise NotImplementedError('FACTS AS LANDMARK NOT IMPLEMENTED YET')
            else:
                if not model.progress_tracker.check_operation_carried_out(l):
                    missing_landmarks += 1
        return missing_landmarks

    def presolving_processing(self, **kwargs) -> None:
        assert 'initial_model' in kwargs
        initial_model = kwargs['initial_model']

        if isinstance(initial_model.current_state, StateNovelty):
            default_seen_elements = copy.copy(StateNovelty.seen_elements)

        self.calculate_reachability(initial_model)

        if isinstance(initial_model.current_state, StateNovelty):
            StateNovelty.seen_elements = default_seen_elements

        root_node = AndNode('LandMarkRootNode')
        self.tree.add_root_node(root_node)
        initial_tasks = self.problem.get_subtasks()
        for i in initial_tasks:
            p_index = 0
            for p in i.task.parameters:
                i.given_params[p.name] = i.parameters[p_index]
                p_index += 1
            self._add_to_node(i, root_node)
        # Landmark extraction from tree
        self._extract_landmarks()
        # print('Number of Landmarks Found: {}'.format(len(root_node.landmarks)))

    def calculate_reachability(self, initial_model):
        delete_relaxed = DeleteRelaxed(self.domain, self.problem, self.solver, self.search_models)
        delete_relaxed.presolving_processing()
        goal_distance_estimate, self.reachability = delete_relaxed.ranking(initial_model, returnAltState=True)
        self.alt_problem, self.alt_domain = delete_relaxed.alt_problem, delete_relaxed.alt_domain
        self.method_reachability = delete_relaxed._found_methods

    def _extract_landmarks(self):
        """Recursive strategy where we begin by calculating the landmarks for the children of the root
        If the node needs the landmarks of some children to be computed we recur and calculate the children's landmarks
        """
        # for r in self.tree.root.requires:
        #     r.calculate_landmarks()
        # self.tree.root.calculate_landmarks()
        # self.tree.root.landmarks.remove('LandMarkRootNode')
        # non_calculated_nodes = list(self.tree.nodes.values())

        # Set landmarks for initial facts
        for f in self.problem.initial_state.elements:
            initial_fact_node_name = 'FACT--' + str(f).replace(" - ", "-").replace(' ', '-')
            initial_fact_node = self.tree.get_existing_node(initial_fact_node_name)
            if initial_fact_node is not None:
                self.tree.leaf_nodes.add_leaf_node(initial_fact_node)

        # Iterate until no nodes can have landmarks calculated
        while self.tree.leaf_nodes:
            # Get a node that needs landmarks calculated
            leaf_node, leaf_node_upwards_recur_set = self.tree.leaf_nodes.pop_leaf_node()
            leaf_node_upwards_recur_set.add(leaf_node.name)
            already_seen_node = leaf_node.landmarks_calculated

            leaf_node.calculate_landmarks()

            # Remove from non_calculated set - TODO: Remove this
            # if leaf_node in non_calculated_nodes:
            #     non_calculated_nodes.remove(leaf_node)

            # Calculate / Recalculate upwards nodes
            for r in leaf_node.required_by + leaf_node.provides:
                if type(r) == OrNode:
                    # if any([x.landmarks_calculated for x in r.requires]) and r.get_child_landmark_calculated_num() > \
                    #         r.previous_landmark_calculate_positives:
                    if any([x.landmarks_calculated for x in r.requires]) and \
                            (r.hash_child_list() != r.child_list_hash or r.child_list_hash is None):
                        self.tree.leaf_nodes.add_leaf_node(r)
                elif type(r) == FactNode:
                    # if any([x.landmarks_calculated for x in r.provided_by]) and \
                    #         r.get_child_landmark_calculated_num() > r.previous_landmark_calculate_positives:
                    if any([x.landmarks_calculated for x in r.provided_by]) and (r.hash_child_list() != r.child_list_hash or r.child_list_hash is None):
                        self.tree.leaf_nodes.add_leaf_node(r)
                elif type(r) == AndNode:
                    # if all([x.landmarks_calculated for x in r.requires]) and \
                    #         all([x.landmarks_calculated for x in r.provided_by]) and \
                    #         r.get_child_landmark_calculated_num() > r.previous_landmark_calculate_positives:
                    if all([x.landmarks_calculated for x in r.requires]) and \
                            all([x.landmarks_calculated for x in r.provided_by]) and \
                            (r.hash_child_list() != r.child_list_hash or r.child_list_hash is None):
                        self.tree.leaf_nodes.add_leaf_node(r)

            # If this is not the first time calculating the landmarks for this node we need to update nodes upwards in the tree
            if already_seen_node:
                for r in leaf_node.required_by:
                    if r.landmarks_calculated and r.name not in leaf_node_upwards_recur_set:
                    # child_list_hash = r.hash_child_list()
                    # if r.landmarks_calculated and child_list_hash != r.child_list_hash:
                        self.tree.leaf_nodes.add_leaf_node(r, leaf_node_upwards_recur_set, priority=True)

        # root = self.tree.root     # For Debugging
        # print(root.landmarks)
        assert self.tree.root.landmarks_calculated

    def _add_to_node(self, task, parent_node):
        if not parent_node.in_already_seen(task):
            # Get / Create a node for the task
            node_name = str(task)
            if type(task.task) == Task:
                node, existed = self.tree.get_node(node_name, 'OR', parent_node)
            else:
                node, existed = self.tree.get_node(node_name, 'AND', parent_node)

            # Add new node as a requirement of parent node
            parent_node.add_to_requires(node)
            parent_node.add_to_already_seen(task)
            node.add_to_required_by(parent_node)
            if parent_node in self.tree.leaf_nodes:
                self.tree.leaf_nodes.remove_leaf_node(parent_node)

            if not existed:
                # Recur
                if type(task.task) == Task:
                    # Create new node for each method
                    self._expand_task(task, node)
                elif type(task.task) == Method:
                    # Create new node for each subtask
                    self._expand_method(task, node)
                else:
                    # Task is an action
                    self._expand_action(task, node)

    def _add_fact_to_node(self, fact: str, node, operation: str):
        fact_node, existed = self.tree.get_node(fact, 'FACT', None)
        if operation == "PROVIDES":
            node.add_to_provides(fact_node)
            fact_node.add_to_provided_by(node)
            if fact_node in self.tree.leaf_nodes:
                self.tree.leaf_nodes.remove_leaf_node(fact_node)
        elif operation == "REQUIRES":
            node.add_to_requires(fact_node)
            node.add_to_already_seen(fact)
            fact_node.add_to_required_by(node)
            if node in self.tree.leaf_nodes:
                self.tree.leaf_nodes.remove_leaf_node(node)
        else:
            raise ValueError("Unknown Fact Operation: {}".format(operation))

    def _expand_task(self, task, node):
        for method in task.task.methods:
            parameters = {}
            i = 0
            for k in task.given_params.keys():
                parameters[method.task['params'][i].name] = task.given_params[k]
                i += 1

            param_options = self.allParameters.get_potential_parameters(method, parameters, None)

            for param_option in param_options:
                subtask_name = method.name
                for p in param_option:
                    subtask_name += "-" + param_option[p].name

                if subtask_name in self.method_reachability:
                    subT = Subtask(method, method.parameters)
                    subT.add_given_parameters(param_option)
                    self._add_to_node(subT, node)

    def _expand_method(self, task, node):
        subtasks = task.task.get_subtasks()
        if subtasks:
            subtasks = task.task.get_subtasks().get_tasks()
        else:
            subtasks = []

        for mod in subtasks:
            mod = Subtask(mod.task, mod.parameters)

            # Check parameter count
            parameters = {}
            param_keys = [p.name for p in mod.parameters]
            action_keys = [p.name for p in mod.task.parameters]
            if len(action_keys) > 0:
                for j in range(len(action_keys)):
                    try:
                        parameters[action_keys[j]] = task.given_params[param_keys[j]]
                    except IndexError:
                        pass
                    except KeyError as e:
                        if param_keys[j][0] != "?" and param_keys[j] in self.problem.objects:
                            parameters[action_keys[j]] = self.problem.get_object(param_keys[j])
                        else:
                            raise KeyError(e)
            else:
                for j in range(len(param_keys)):
                    parameters[param_keys[j]] = task.given_params[param_keys[j]]

            mod.add_given_parameters(parameters)

            # Recur
            self._add_to_node(mod, node)

    def _expand_action(self, task, node):
        # Facts which are added need to be represented as nodes
        effects = task.task.effects.effects
        for e in effects:
            if not e.negated:
                fact = "FACT--{}".format(e.predicate.name)
                for p in e.parameters:
                    fact += "-{}".format(task.given_params[p].name)
                self._add_fact_to_node(fact, node, 'PROVIDES')

        conditions = task.task.preconditions.get_positive_predicate_conditions()
        for c in conditions:
            fact = "FACT--{}".format(c.pred.name)
            for p in c.parameter_name:
                fact += "-{}".format(task.given_params[p].name)
            self._add_fact_to_node(fact, node, 'REQUIRES')
