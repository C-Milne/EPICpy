from Internal_Representation.precondition import Precondition
from Internal_Representation.modifier import Modifier
from Internal_Representation.action import Action
from Internal_Representation.method import Method
from Internal_Representation.task import Task
from Internal_Representation.predicate import Predicate
from Internal_Representation.Type import Type
from Internal_Representation.derived_predicate import DerivedPredicate


class Domain:
    def __init__(self, problem):
        self.actions = {}
        self.methods = {}
        self.tasks = {}
        self.types = {}
        self.predicates = {}
        self.derived_predicates = {}
        self.constants = {}
        self.constant_names = set()
        self.problem = problem

    def add_action(self, action):
        assert type(action) == Action
        self.actions[action.name] = action

    def add_method(self, method, add_to_task=True):
        assert type(method) == Method
        if method.name in self.methods:
            raise NameError("Method Name 'swap_ob_1' is Already Assigned")
        self.methods[method.name] = method
        if not method.task is None and add_to_task:
            self._add_method_to_task(method, method.task['task'])

    def add_task(self, task: Task):
        assert type(task) == Task
        self.tasks[task.name] = task

    def add_predicate(self, predicate: Predicate):
        assert type(predicate) == Predicate
        assert predicate.name not in self.predicates.keys()
        if predicate.name not in self.derived_predicates:
            self.predicates[predicate.name] = predicate

    def add_derived_predicate(self, derived_predicate: DerivedPredicate):
        assert type(derived_predicate) == DerivedPredicate
        assert derived_predicate.name not in self.derived_predicates.keys()
        if derived_predicate.name in self.predicates:
            del self.predicates[derived_predicate.name]
        self.derived_predicates[derived_predicate.name] = derived_predicate

    def add_type(self, t):
        assert type(t) == Type
        # Check type is not already defined
        if t.name not in self.types.keys():
            self.types[t.name] = t
        else:
            for p in t.parents:
                self.types[t.name].add_parent(p)

    def add_constant(self, constant):
        self.constants[constant.name] = constant
        self.constant_names.add(constant.name)

    def get_action(self, action_name):
        """Return an actions object
        :params     - action_name : name of object to be returned
        :returns    - action object : if can be found
                    - False : otherwise"""
        try:
            return self.actions[action_name]
        except Exception:
            # Could not find action
            pass
        return False

    def get_all_actions(self):
        action_list = []
        for x in self.actions:
            action_list.append(self.actions[x])
        return action_list

    def get_task(self, name):
        if name in self.tasks.keys():
            # Compare parameters given with parameters of task
            return self.tasks[name]
        return None

    def get_all_tasks(self):
        return self.tasks

    def get_task_methods(self, task: str):
        if type(task) == str:
            task = self.get_task(task)
        return task.methods

    def get_type(self, name):
        if name in self.types:
            return self.types[name]
        else:
            return False

    def get_method(self, method_name):
        if not method_name in self.methods.keys():
            return None
        return self.methods[method_name]

    def get_all_methods(self):
        method_list = []
        for x in self.methods:
            method_list.append(self.methods[x])
        return method_list

    def get_modifier(self, name):
        if name in self.methods.keys():
            return self.methods[name]
        elif name in self.tasks.keys():
            return self.tasks[name]
        elif name in self.actions.keys():
            return self.actions[name]
        else:
            return None

    def get_predicate(self, name):
        if name not in self.predicates.keys():
            return self.get_derived_predicate(name)
        return self.predicates[name]

    def get_derived_predicate(self, name):
        if name not in self.derived_predicates.keys():
            return None
        return self.derived_predicates[name]

    def get_constant(self, name):
        if name in self.constant_names:
            return self.constants[name]
        return None

    def name_assigned(self, str):
        """TODO : Test this with all components"""
        """:param   - str : string being checked
            :returns    - True : if str is already in use
                        - False : otherwise"""
        if str in self.methods.keys() or str in self.tasks.keys() or str in self.actions.keys():
            return True
        return False

    def add_problem(self, problem):
        self.problem = problem

    def _add_method_to_task(self, method, task):
        assert type(method) == Method
        assert type(task) == Task
        task.add_method(method)
