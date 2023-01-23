from Internal_Representation.Type import Type


class Object:
    def __init__(self, name, ob_type: Type = None):
        assert type(name) == str
        self.name = name
        assert type(ob_type) == Type or ob_type is None
        self.type = ob_type

    def set_type(self, t):
        assert type(t) == Type
        self.type = t

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif self.name != other.name:
            return False
        elif self.type != other.type:
            return False
        return True

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
