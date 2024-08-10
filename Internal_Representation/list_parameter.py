from Internal_Representation.parameter import Parameter


class ListParameter(Parameter):
    """
    This class is used to express the concept of list parameters, an example of which can be found in the
    JSHOP blocks domain. (:method (assert-goals (?goal . ?goals))
    """
    def __init__(self, name: str, internal_param_name: str = None):
        super().__init__(name)
        assert type(internal_param_name) == str or internal_param_name is None
        self.internal_param_name = internal_param_name
        self.list = []

    def add_to_list(self, v):
        self.list.append(v)

    def pop(self):
        if len(self.list) > 0:
            return self.list.pop(0)
        return None
