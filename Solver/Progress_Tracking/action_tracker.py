from Internal_Representation.modifier import Modifier
from Internal_Representation.Object import Object
from Internal_Representation.list_parameter import ListParameter


class ActionTracker:
    def __init__(self, mod: Modifier, parameters_used: dict):
        assert isinstance(mod, Modifier)
        assert type(parameters_used) == dict
        for k in parameters_used:
            assert type(parameters_used[k]) == Object or type(parameters_used[k]) == ListParameter
        self.mod = mod
        self.parameters_used = parameters_used

    def __eq__(self, other):
        if self.mod != other.mod:
            return False
        if len(self.parameters_used) != len(other.parameters_used):
            return False
        for i in self.parameters_used:
            if not i in other.parameters_used:
                return False
            elif self.parameters_used[i] != other.parameters_used[i]:
                return False
        return True

    def __str__(self):
        return_str = "{}".format(self.mod.name)
        if len(self.parameters_used) > 0:
            return_str += " -"
            for k in self.parameters_used:
                return_str += " {}".format(self.parameters_used[k])
        return return_str
