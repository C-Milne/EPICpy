import sys
from abc import ABC, abstractmethod, ABCMeta
from Solver.Models.model import Model
from Solver.Search_Queues.search_queue import SearchQueue
from Internal_Representation.method import Method
from Internal_Representation.action import Action, Effects
from Internal_Representation.task import Task
from Internal_Representation.reg_parameter import RegParameter
from Internal_Representation.subtasks import Subtasks
from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.state import State
from Internal_Representation.list_parameter import ListParameter

"""Space for importing heuristic functions"""
from Solver.Heuristics.Heuristic import Heuristic
from Solver.Heuristics.pruning import Pruning

"""Space for importing parameter selection functions"""
from Solver.Parameter_Selection.ParameterSelector import ParameterSelector
from Solver.Parameter_Selection.Requirement_Selection import RequirementSelection, \
    Requirements  # Do not remove this import statement

"""Space for importing progress_tracker classes"""
from Solver.Progress_Tracking.progress_tracker import ProgressTracker
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker

"""Importing from sys modules"""
Precondition = sys.modules['Internal_Representation.precondition'].Precondition
ForallCondition = sys.modules['Internal_Representation.conditions'].ForAllCondition


class Solver(ABC):
    ModelClass = Model

    def __init__(self, domain, problem):
        self.domain = domain
        self.problem = problem

        self.search_models = SearchQueue()
        heuristic = Pruning(self.domain, self.problem, self, self.search_models)
        self.search_models.add_heuristic(heuristic)

        self.parameter_selector = RequirementSelection(self)
        self._requirement_parameter_selector = RequirementSelection(self)
        self.progress_tracker = SequentialTracker
        self.task_expansion_given_param_check = True

    def set_heuristic(self, heuristic):
        if type(heuristic) == type or type(heuristic) == ABCMeta:
            heuristic = heuristic(self.domain, self.problem, self, self.search_models)
        assert isinstance(heuristic, Heuristic)
        self.search_models.add_heuristic(heuristic)

    def set_parameter_selector(self, selector):
        if type(selector) == type or type(selector) == ABCMeta:
            selector = selector(self)
        assert isinstance(selector, ParameterSelector)
        self.parameter_selector = selector

    def set_search_queue(self, search_queue):
        if type(search_queue) == type or type(search_queue) == ABCMeta:
            search_queue = search_queue()
        assert isinstance(search_queue, SearchQueue) or isinstance(type(search_queue), type(SearchQueue))
        heu = self.search_models.heuristic
        self.search_models = search_queue
        self.search_models.add_heuristic(heu)

    def set_model_class(self, model_class):
        # TODO : Assert type here
        Solver.ModelClass = model_class

    def set_progress_tracker(self, progress_tracker):
        assert issubclass(progress_tracker, ProgressTracker)
        self.progress_tracker = progress_tracker

    def solve(self, **kwargs):
        self.parameter_selector.presolving_processing(self.domain, self.problem)
        self.search_models.heuristic.presolving_processing()
        subtasks_orderings = self.problem.subtasks.get_task_orderings()

        printed_subtasks = False

        for subtasks in subtasks_orderings:
            list_subT = []
            num_tasks = len(subtasks)
            task_counter = 0
            while task_counter < num_tasks:
                subT = subtasks[task_counter]
                if subT == "and" or subT == "or":
                    del subtasks[task_counter]
                    num_tasks -= 1
                    continue

                if not printed_subtasks:
                    print("Subtask:", task_counter, "-", subT.get_name() + str([p.name for p in subT.parameters]))

                # Create initial search model
                param_dict = self._generate_param_dict(subT.task, subT.parameters)
                subT.add_given_parameters(param_dict)
                list_subT.append(subT)
                task_counter += 1
            printed_subtasks = True

            if len(list_subT) == 1:
                waiting_subT = []
            else:
                waiting_subT = list_subT[1:]
                list_subT = [list_subT[0]]

            initial_model = self.ModelClass(State.reproduce(self.problem.initial_state), list_subT, self.problem,
                                       waiting_subT, progress_tracker_class=self.progress_tracker, initial_model=True)

            self.search_models.add(initial_model)

        if "search" in kwargs:
            search = kwargs["search"]
        else:
            search = True

        if search != False:
            return self._search()

    def _search(self, step_control=False):
        """:parameter   - step_control  - If True, then loop will only execute once"""
        while True:
            # New model to operate on
            search_model = self.search_models.pop()
            if search_model is None:
                return None

            # Check what needs to be done to this model
            next_modifier = search_model.get_next_modifier()
            assert type(next_modifier) == Subtasks.Subtask

            if type(next_modifier.task) == Task:
                self._expand_task(next_modifier, search_model)
            elif type(next_modifier.task) == Method:
                self._expand_method(next_modifier, search_model)
            elif type(next_modifier.task) == Action:
                self._expand_action(next_modifier, search_model)
            else:
                raise NotImplementedError

            # Loop exit conditions
            if self.search_models.get_num_search_models() == 0 and self.search_models.get_num_completed_models() == 0:
                return None
            elif step_control:
                break
            elif self.search_models.get_num_completed_models() > 0:
                for m in self.search_models.get_completed_models():
                    eval = self.problem.evaluate_goal(m)
                    if eval is None or eval == True:
                        m.num_models_used = Model.model_counter
                        return m
                self.search_models.clear_completed_models()

    @abstractmethod
    def _expand_task(self, subtask: Subtasks.Subtask, search_model: Model):
        """
        :param subtask: Subtask object containing info in the task being expanded
        :param search_model: Model object the task is being applied to
        :return: None
        This method needs to be expanded to accommodate processing tasks"""
        raise NotImplementedError

    @abstractmethod
    def _expand_method(self, subtask: Subtasks.Subtask, search_model: Model):
        """
        :param subtask: Subtask object containing info in the method being expanded
        :param search_model: Model object the method is being applied to
        :return: None
        This method needs to be expanded to accommodate processing methods"""
        raise NotImplementedError

    @abstractmethod
    def _expand_action(self, subtask: Subtasks.Subtask, search_model: Model):
        """
        :param subtask: Subtask object containing info in the action being expanded
        :param search_model: Model object the action is being applied to
        :return: None
        This method needs to be expanded to accommodate processing actions"""
        raise NotImplementedError

    def _generate_param_dict(self, modifier, params):
        """
        :param modifier: Modifier
        :param params: List [Object]
        :return: dict [Object]
        """
        assert type(modifier) == Method or type(modifier) == Action or type(modifier) == Task
        # Check number of params is the amount expected
        if type(params) == ListParameter:
            len_params = 1
        else:
            len_params = len(params)

        if type(params) == ListParameter:
            param_dict = {modifier.get_parameters()[0].name: params}
        else:
            # Map params to self.parameters
            i = 0
            param_dict = {}
            while i < modifier.get_number_parameters():
                param_name = modifier.parameters[i]
                if type(param_name) == RegParameter:
                    param_name = param_name.name
                try:
                    param_dict[param_name] = params[i]
                except:
                    pass
                i += 1
        return param_dict

    def compute_derived_predicates(self, search_model: Model):
        # Remove derived predicates from search model state

        # Check derived predicates
        for i in self.domain.derived_predicates:
            pred = self.domain.derived_predicates[i]
            assert len(pred.conditions) == len(pred.cond_requirements)
            found_predicates = []  # Used to make sure only one of each combination of variables is selected

            for j in range(len(pred.conditions)):
                # Choose variables
                found_params = self._requirement_parameter_selector._find_satisfying_parameters(search_model,
                                                                                                pred.cond_requirements[
                                                                                                    j])
                for param_option in found_params:
                    # Evaluate predicate
                    result = pred.conditions[j].evaluate(param_option, search_model, self.problem)
                    if result and param_option not in found_predicates:
                        found_predicates.append(param_option)
                        obs = self.convert_param_dict_to_list(param_option, pred.parameters)
                        search_model.current_state.add_element(ProblemPredicate(pred, obs))

    @staticmethod
    def check_duplicate_values_dictionary(d: dict) -> bool:
        """https://www.geeksforgeeks.org/python-find-keys-with-duplicate-values-in-dictionary/
        :returns True if a duplicate is present
        :returns False if there is no duplicates"""
        flipped = {}
        for key, value in d.items():
            if value not in flipped:
                flipped[value] = [key]
            else:
                return True
        return False

    @staticmethod
    def reproduce_dict(d: dict):
        return_dict = {}
        keys = list(d.keys())
        for k in keys:
            return_dict[k] = d[k]
        return return_dict

    @staticmethod
    def convert_param_dict_to_list(param_dict, parameters: list):
        return_list = []
        for i in parameters:
            return_list.append(param_dict[i.name])
        return return_list

    @staticmethod
    def reproduce_parameter_list(param_list):
        new_list = []
        for p in param_list:
            new_list.append(p)
        return new_list

    @staticmethod
    def reproduce_state(state):
        return State.reproduce(state)

    def reproduce_model(self, model, search_mods=None):
        """
        :param model: Model
        :param search_mods: List [Subtasks.Subtask]
        :return: Model
        """
        return model.reproduce(self.problem, search_mods)

    @staticmethod
    def output(resulting_model: Model):
        assert isinstance(resulting_model, Model) or resulting_model is None

        if not resulting_model is None:
            print(resulting_model.get_progress_tracker())
            # print("\nFinal State:")
            # print(resulting_model.current_state)

            print("\nSearch Models Created During Search: {}".format(resulting_model.num_models_used))
        else:
            print("plan not found")
