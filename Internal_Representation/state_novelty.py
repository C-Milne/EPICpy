import copy
from Internal_Representation.state import State, ProblemPredicate


class StateNovelty(State):
    def __init__(self):
        super().__init__()
        self._seen_elements = set()
        self._seen_element_pairs = set()

    def add_element(self, element: ProblemPredicate) -> bool:
        assert type(element) == ProblemPredicate
        novel = False
        if element not in self:
            self.elements.append(element)
            self._add_element_to_index(element)
            element_hash = hash(element)

            if element_hash not in self._seen_elements:
                novel = True
                self._seen_elements.add(element_hash)
            # TODO: Add novelty for the element pairs
        return novel

    def load_from_default_state(self, state: State):
        for e in state.elements:
            self.add_element(e)

    def reproduce(self):
        new_state = StateNovelty()
        new_state.elements = [*self.elements]
        new_state._index = copy.deepcopy(self._index)
        new_state._seen_elements = set()
        new_state._seen_elements.update(self._seen_elements)
        new_state._seen_element_pairs = set()
        new_state._seen_element_pairs.update(self._seen_element_pairs)
        return new_state
