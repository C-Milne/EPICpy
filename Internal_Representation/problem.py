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

    def set_name(self, name: str):
        assert type(name) == str
        self.name = name

    def add_object(self, ob):
        if type(ob) == list:
            for i in ob:
                self.add_object(i)
        else:
            assert type(ob) == Object
            self.objects[ob.name] = ob

    def add_to_initial_state(self, v: ProblemPredicate):
        assert type(v) == ProblemPredicate
        self.initial_state.add_element(v)

    def add_subtasks(self, sub_tasks):
        assert type(sub_tasks) == Subtasks
        self.subtasks = sub_tasks

    def order_subtasks(self, orderings):
        self.subtasks.order_subtasks(orderings)

    def get_object(self, name):
        if name in self.objects:
            return self.objects[name]
        return None

    def get_objects_of_type(self, param_type):
        if type(param_type) == str:
            param_type = self.domain.get_type(param_type)
        if type(param_type) == Type:
            returnObs = []
            for o in self.objects:
                if self.objects[o].type == param_type:
                    returnObs.append(self.objects[o])

            return returnObs
        elif param_type is None:
            return self.objects
        else:
            raise TypeError("Unexpected type {}".format(type(param_type)))

    def get_all_objects(self):
        return self.objects

    def get_subtasks(self):
        if self.subtasks is None:
            return None
        return self.subtasks.get_tasks()

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
