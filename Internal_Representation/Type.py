class Type:
    def __init__(self, name, parent=None):
        assert type(name) == str
        self.name = name
        assert type(parent) == Type or parent is None
        if parent is None:
            self.parents = []
        else:
            self.parents = [parent]
        self.satisfying_objects = []

    def add_parent(self, p):
        if p not in self.parents:
            self.parents.append(p)

    def add_satisfying_object(self, ob):
        self.satisfying_objects.append(ob)
        for p in self.parents:
            p.add_satisfying_object(ob)

    def __str__(self):
        return self.name
