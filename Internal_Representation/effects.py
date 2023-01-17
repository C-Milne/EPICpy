from Internal_Representation.predicate import Predicate
from Internal_Representation.parameter import Parameter
from Internal_Representation.precondition import Precondition


class Effects:
    class Effect:
        def __init__(self, predicate, parameters, negated):
            self.predicate = predicate
            self.parameters = parameters
            self.negated = negated

    class RunTimeEffect:
        def __init__(self, parameter):
            self.parameters = parameter

    class ForAllEffect:
        def __init__(self, parameter, precondition, negated):
            self.parameters = parameter
            self.precondition = precondition
            self.effects = []
            self.negated = negated

        def add_effect(self, effect):
            assert isinstance(effect, Effects.Effect)
            self.effects.append(effect)

    def __init__(self):
        self.effects = []

    def add_effect(self, predicate: Predicate, parameters: list = [], negated: bool = False):
        """Params:  - predicate : name of predicate to be modified
                    - parameters : list of parameters belonging to predicate
                    - negated : True if 'not' statement encapsulates effect
                              : False otherwise"""
        assert type(predicate) == Predicate
        assert type(parameters) == list
        for p in parameters:
            assert type(p) == str
        assert type(negated) == bool
        self.effects.append(self.Effect(predicate, parameters, negated))

    def add_runtime_effect(self, parameter: str):
        """(:operator (!!assert ?g)
               ()
               ()
               (?g)
        :param parameter = '?g'
        """
        assert type(parameter) == str
        self.effects.append(self.RunTimeEffect(parameter))

    def add_forall_effect(self, parameter: Parameter, preconditions: Precondition, effects, negated: bool):
        for_ef = self.ForAllEffect(parameter, preconditions, negated)
        for e in effects:
            assert isinstance(e, self.Effect)
            for_ef.add_effect(e)
        self.effects.append(for_ef)

    def __len__(self):
        return len(self.effects)
