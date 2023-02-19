import copy
from itertools import combinations
from Internal_Representation.state import State, ProblemPredicate, Predicate


class StateNovelty(State):
    MaxNoveltyLevel = 1

    def __init__(self):
        super().__init__()
        self._seen_elements = set()
        self._seen_element_pairs = set()
        self._element_hashes = []   # stores hashes of elements in the state. For levels of novelty > 1

    def add_element(self, element: ProblemPredicate) -> int:
        assert type(element) == ProblemPredicate
        novel = None
        if element not in self.elements:
            element_hash = hash(element)

            if element_hash not in self._seen_elements:
                novel = self.MaxNoveltyLevel
                self._seen_elements.add(element_hash)

            # TODO: When retying novelty level > 1 check all this code - refactor preferred
            def _create_hash_list(element_hash_from_list):
                return hash(frozenset([element_hash, *element_hash_from_list]))

            for level in range(2, self.MaxNoveltyLevel + 1):
                # Each combination of choosing level - 1 elements from the state elements
                element_combos = list(combinations(self._element_hashes, level - 1))
                level_hashes = set(map(_create_hash_list, element_combos))
                initial_size = len(self._seen_element_pairs)
                self._seen_element_pairs = self._seen_element_pairs.union(level_hashes)
                if initial_size < len(self._seen_element_pairs) and not novel:
                    novel = self.MaxNoveltyLevel + 1 - level

            # Novelty procedure is ABOVE this
            self.elements.append(element)
            self._add_element_to_index(element)
            self._element_hashes.append(element_hash)
        return novel

    def _remove_element_objects(self, predicate: Predicate, predicate_objects):
        """Params:  - predicate : Predicate
                    - predicate_objects : [Object] - List of objects taken as parameters"""
        predicate_indexes = self.get_indexes(predicate.name)
        if predicate_indexes is None:
            return
        deletion = False
        for i in predicate_indexes:
            element_objects = self.elements[i].objects
            if element_objects == predicate_objects:
                del self.elements[i]
                deletion = True
                break
        # Adjust self._index
        if deletion:
            self._adjust_index_remove_element(predicate.name, i)
            self._remove_from_element_hashes(i)

    def _remove_element_no_objects(self, predicate: Predicate):
        """Params:  - predicate : Predicate"""
        index = self.get_indexes(predicate.name)
        assert len(index) == 1
        index = index[0]

        # Do the deletion
        del self.elements[index]

        # Adjust self._index
        self._adjust_index_remove_element(predicate.name, index)
        self._remove_from_element_hashes(index)

    def _remove_from_element_hashes(self, i):
        self._element_hashes.pop(i)

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
        new_state._element_hashes = [*self._element_hashes]
        return new_state

    def set_max_novelty_level(self, level: int):
        assert level > 0
        StateNovelty.MaxNoveltyLevel = level
