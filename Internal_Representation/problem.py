import itertools
from Internal_Representation.Object import Object
from Internal_Representation.state import State
from Internal_Representation.Type import Type
from Internal_Representation.precondition import Precondition
from Solver.Models.default_model import DefaultModel
from Internal_Representation.subtasks import Subtasks
from Internal_Representation.problem_predicate import ProblemPredicate


class Problem:
    def __init__(self, domain):
        self.name = None
        self.objects = {}
        self.initial_state = State()
        self.subtasks = None
        self.domain = domain
        self.goal_conditions = None
        self._initial_task_network_parameters = None
        self.initial_subtask_orderings = None
        self._subtasks_before_ordering = []

    def set_name(self, name: str):
        assert type(name) == str
        self.name = name

    def add_object(self, ob, add_type_satisfying=True):
        if type(ob) == list:
            for i in ob:
                self.add_object(i, add_type_satisfying)
        else:
            assert type(ob) == Object
            self.objects[ob.name] = ob
            if add_type_satisfying:
                if ob.type is not None:
                    ob.type.add_satisfying_object(ob)

    def add_to_initial_state(self, v: ProblemPredicate):
        assert type(v) == ProblemPredicate
        self.initial_state.add_element(v, False)

    def add_initial_task_network_parameter(self, parameter_name: str, parameter_type: str):
        if not self._initial_task_network_parameters:
            self._initial_task_network_parameters = {}
        self._initial_task_network_parameters[parameter_name] = parameter_type

    def add_subtasks(self, sub_tasks):
        assert type(sub_tasks) == Subtasks
        self.subtasks = sub_tasks

    def order_subtasks(self):
        if self.subtasks.ordered:
            # If the subtasks are already ordered we dont need to order again
            return
        if len(self._subtasks_before_ordering) > 0:
            full_orderings = []
            for subtasks in self._subtasks_before_ordering:
                subtasks.order_subtasks(self.initial_subtask_orderings)
                full_orderings += subtasks.get_task_orderings()
            self.subtasks.task_orderings = full_orderings
        else:
            self.subtasks.order_subtasks(self.initial_subtask_orderings)

    def set_initial_subtask_ordering(self, orderings):
        self.initial_subtask_orderings = orderings

    def get_object(self, name):
        if name in self.objects:
            return self.objects[name]
        return None

    def get_objects_of_type(self, param_type):
        if type(param_type) == str:
            param_type = self.domain.get_type(param_type)
        if type(param_type) == Type:
            return param_type.satisfying_objects
        elif param_type is None:
            return self.objects.values()
        else:
            raise TypeError("Unexpected type {}".format(type(param_type)))

    def get_all_objects(self):
        return self.objects

    def get_subtasks(self):
        if self.subtasks is None:
            return None
        return self.subtasks.get_tasks()

    def get_constant(self, ob_name) -> KeyError:
        const = self.domain.get_constant(ob_name)
        if const is None:
            raise KeyError('Constant {} not found!'.format(ob_name))
        return const

    def add_goal_conditions(self, cons):
        assert type(cons) == Precondition
        self.goal_conditions = cons

    def evaluate_goal(self, model: DefaultModel):
        if self.goal_conditions is None:
            return None
        return self.goal_conditions.evaluate(self.objects, model, self)

    def has_goal_conditions(self):
        if self.goal_conditions is None:
            return False
        return True

    def has_initial_task_network_parameters(self):
        if not self._initial_task_network_parameters:
            return False
        return True

    def ground_initial_subtasks(self):
        parameter_ordering = []
        for p in self._initial_task_network_parameters:
            self._initial_task_network_parameters[p] = self.get_objects_of_type(self._initial_task_network_parameters[p])
            parameter_ordering.append(p)
        vals = list(self._initial_task_network_parameters.values())
        combs = list(itertools.product(*vals))

        for c in combs:
            # Reproduce self.subtasks
            new_subtasks = self.subtasks.reproduce()
            # Assign objects to parameters for each combination
            for subtask in new_subtasks.tasks:
                for p_i in range(len(subtask.parameters)):
                    p = subtask.parameters[p_i]
                    if type(p) == str:
                        subtask.parameters[p_i] = c[parameter_ordering.index(p)]
            self._subtasks_before_ordering.append(new_subtasks)
