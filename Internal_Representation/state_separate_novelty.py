import copy
from Internal_Representation.state_novelty import StateNovelty, ProblemPredicate


class StateSeparateNovelty(StateNovelty):
    score_seen_elements = {}

    def __init__(self):
        super().__init__()
        self._not_checked_facts = []

    def add_element(self, element: ProblemPredicate, check_presence=True):
        add_to_state = self._add_element_check_add_to_state(element, check_presence)

        if add_to_state:
            # Novelty procedure is ABOVE this
            self.elements.append(element)
            self._add_element_to_index(element)
            self._not_checked_facts.append(element)

    def _add_element_check_add_to_state(self, element, check_presence) -> bool:
        assert type(element) == ProblemPredicate
        add_to_state = True
        if check_presence:
            add_to_state = element not in self
        else:
            element_hash = hash(element)
            StateNovelty.seen_elements.add(element_hash)
        return add_to_state

    def check_novelty_not_checked_facts(self, hamming_score):
        novelty = 0
        for e in self._not_checked_facts:
            novel = self._check_element_novelty_separate(e, hamming_score)
            if novel and novel > novelty:
                novelty = novel

        return novelty

    def _check_element_novelty_separate(self, element, hamming_score):
        novel = None
        element_hash = hash(element)

        if hamming_score not in StateSeparateNovelty.score_seen_elements:
            StateSeparateNovelty.score_seen_elements[hamming_score] = set()

        if element_hash not in StateSeparateNovelty.score_seen_elements[hamming_score]:
            novel = self.MaxNoveltyLevel
            StateSeparateNovelty.score_seen_elements[hamming_score].add(element_hash)
        StateNovelty.seen_elements.add(element_hash)
        return novel

    def _remove_from_element_hashes(self, i):
        pass

    def reproduce(self):
        new_state = StateSeparateNovelty()
        new_state.elements = [*self.elements]
        new_state._index = copy.deepcopy(self._index)
        return new_state

    def initialise(self):
        super().initialise()
        StateSeparateNovelty.score_seen_elements = {}
