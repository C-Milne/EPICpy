import copy
from itertools import combinations
from Internal_Representation.state import State, ProblemPredicate, Predicate


class StateNovelty(State):
    MaxNoveltyLevel = 1
    seen_elements = set()
    seen_element_pairs = set()

    def __init__(self):
        super().__init__()
        self.element_hashes = []  # stores hashes of elements in the state. For levels of novelty > 1

    def initialise(self):
        StateNovelty.seen_elements = set()
        StateNovelty.seen_element_pairs = set()

    def add_element(self, element: ProblemPredicate, check_presence=True) -> int:
        novel = None
        add_to_state = self._add_element_check_add_to_state(element, check_presence)

        if add_to_state:
            element_hash, novel = self._check_element_novelty(element)

            # Novelty procedure is ABOVE this
            self.elements.append(element)
            self._add_element_to_index(element)
            self.element_hashes.append(element_hash)
        return novel

    def _add_element_check_add_to_state(self, element, check_presence) -> bool:
        assert type(element) == ProblemPredicate
        add_to_state = True
        if check_presence:
            add_to_state = element not in self
        return add_to_state

    def _check_element_novelty(self, element):
        element_hash, novel = self._check_element_novelty_level1(element)
        novel = self._check_element_novelty_other_levels(element_hash, novel)
        return element_hash, novel

    def _check_element_novelty_level1(self, element):
        novel = None
        element_hash = hash(element)

        if element_hash not in StateNovelty.seen_elements:
            novel = self.MaxNoveltyLevel
            StateNovelty.seen_elements.add(element_hash)
        return element_hash, novel

    def _check_element_novelty_other_levels(self, element_hash, novel):
        # TODO: When we come to do novelty for more than level 2 - maybe we should store combinations to save computing time
        # TODO: If we do higher levels of novelty remember to update the diagram for the report
        def _create_hash_list(element_hash_from_list):
            return hash(frozenset([element_hash, *element_hash_from_list]))

        for level in range(2, self.MaxNoveltyLevel + 1):
            # Each combination of choosing level - 1 elements from the state elements
            element_combos = list(combinations(self.element_hashes, level - 1))
            level_hashes = set(map(_create_hash_list, element_combos))
            initial_size = len(StateNovelty.seen_element_pairs)
            StateNovelty.seen_element_pairs = StateNovelty.seen_element_pairs.union(level_hashes)
            if initial_size < len(StateNovelty.seen_element_pairs) and not novel:
                novel = self.MaxNoveltyLevel + 1 - level
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
        self.element_hashes.pop(i)

    def load_from_default_state(self, state: State):
        for e in state.elements:
            self.add_element(e, False)

    def reproduce(self):
        new_state = StateNovelty()
        new_state.elements = [*self.elements]
        new_state._index = copy.deepcopy(self._index)
        new_state.element_hashes = [*self.element_hashes]
        return new_state

    def set_max_novelty_level(self, level: int):
        assert level > 0
        StateNovelty.MaxNoveltyLevel = level
