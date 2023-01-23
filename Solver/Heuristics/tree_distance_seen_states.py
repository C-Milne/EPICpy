import sys
from Solver.Heuristics.seen_states_pruning import SeenStatesPruning
from Solver.Heuristics.tree_distance import Tree
Task = sys.modules['Internal_Representation.task'].Task
Method = sys.modules['Internal_Representation.method'].Method
Action = sys.modules['Internal_Representation.action'].Action
Subtask = sys.modules['Internal_Representation.subtasks'].Subtask
Model = sys.modules['Solver.Models.default_model'].DefaultModel


class TreeDistanceSeenStatesPruning(SeenStatesPruning):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        self.tree = Tree()

    def _inner_ranking(self, model: Model) -> float:
        res = sum(self.tree[x].distance for x in model.get_names_of_task_network_modifiers())
        return res + sum(self.tree[x.task.name].distance for x in model.waiting_subtasks)

    def _calculate_distance_tasks(self, model: Model):
        distance = 0
        for m in model.search_modifiers:
            if type(m) == Task:
                distance += self.tree.nodes[m.name].distance
        for m in model.waiting_subtasks:
            if type(m) == Task:
                distance += self.tree.nodes[m.name].distance
        return distance

    def presolving_processing(self) -> None:
        # Add all actions to tree
        for a in self.domain.get_all_actions():
            node = self.tree.add_node(a.name)
            node.set_distance(1)

        # Create bottom up reachability conditions for methods
        method_reach_conditions = {}
        for m in self.domain.get_all_methods():
            if m.subtasks is None:
                method_reach_conditions[m.name] = []
            else:
                method_reach_conditions[m.name] = list([x.task.name for x in m.subtasks.tasks])

        # Add methods which are bottom up reachable to the tree
        task_nodes = []
        method_nodes = []
        recursive_method_nodes = []
        change = True
        while change:
            change = False
            if len(method_reach_conditions.keys()) == 0:
                break

            del_list = []
            for m in method_reach_conditions:
                m_cons = method_reach_conditions[m]
                # if all_m_cons hold, add m to tree
                if all(x in self.tree.nodes for x in m_cons):
                    method = self.domain.get_method(m)
                    method_node = self.tree.add_node(method.name)
                    task_node = self.tree.add_node(method.task['task'].name, task=True)
                    method_node.parents.append(task_node)

                    if task_node not in task_nodes:
                        task_nodes.append(task_node)
                    task_node.add_child(method_node)
                    method_nodes.append(method_node)

                    if task_node in method_node.children:
                        recursive_method_nodes.append(method_node)

                    for mc in m_cons:
                        mc = self.tree[mc]
                        method_node.add_child(mc)
                        mc.add_parent(method_node)
                    change = True
                    del_list.append(m)

            for m in del_list:
                del method_reach_conditions[m]

        # Assign each task node a distance to goal
        i = 0
        l = len(method_nodes)
        while method_nodes:
            tn = method_nodes.pop(0)
            res = self._calculate_task_node_distance_goal(tn)
            if res is None:
                method_nodes.append(tn)
            else:
                tn.set_distance(res)
                for p in tn.parents:
                    if p.distance is None or p.distance > res + 1:
                        p.distance = res + 1
            i += 1
        for m in recursive_method_nodes:
            res = self._calculate_task_node_distance_goal(m)
            if res != m.distance:
                m.distance = res

    def _calculate_task_node_distance_goal(self, tn) -> int:
        if tn.distance is not None:
            return tn.distance
        else:
            total_distance = 0
            for n in tn.children:
                if n.distance is None:
                    return None
                elif tn == n:
                    continue
                else:
                    total_distance += n.distance
            total_distance += 1
            return total_distance