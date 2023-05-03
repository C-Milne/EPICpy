from Solver.Heuristics.landmarks import Landmarks, AndNode, Subtask


class LandmarksNoReachability(Landmarks):
    def __init__(self, domain, problem, solver, search_models):
        super().__init__(domain, problem, solver, search_models)
        del self.reachability
        del self.method_reachability
        del self.alt_problem
        del self.alt_domain

    def presolving_processing(self, **kwargs) -> None:
        assert 'initial_model' in kwargs
        initial_model = kwargs['initial_model']

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

                subT = Subtask(method, method.parameters)
                subT.add_given_parameters(param_option)
                self._add_to_node(subT, node)