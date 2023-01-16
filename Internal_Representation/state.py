from Internal_Representation.problem_predicate import ProblemPredicate
from Internal_Representation.predicate import Predicate
from Internal_Representation.Object import Object


class State:
    def __init__(self):
        self._index = {}
        self.elements = []

    def add_element(self, element: ProblemPredicate):
        # TODO: When adding an element check that it does not already exist
        assert type(element) == ProblemPredicate
        self.elements.append(element)
        self.__add_element_to_index(element)

    def __add_element_to_index(self, element: ProblemPredicate):
        name = element.predicate.name
        if name in self._index.keys():
            self._index[name].append(len(self.elements) - 1)
        else:
            self._index[name] = [len(self.elements) - 1]

    def get_indexes(self, pred_name: str) -> list:
        if type(pred_name) != str:
            raise TypeError("Parameter 'pred_name' must be a string. Type received: {}".format(type(pred_name)))
        if pred_name in self._index.keys():
            return self._index[pred_name]
        else:
            return None

    def get_element_index(self, index: int) -> ProblemPredicate:
        assert type(index) == int
        if len(self.elements) > index:
            return self.elements[index]
        return None

    def remove_element(self, predicate: Predicate, predicate_objects=None):
        assert type(predicate) == Predicate
        if predicate_objects is None or len(predicate_objects) == 0:
            self.__remove_element_no_objects(predicate)
        else:
            self.__remove_element_objects(predicate, predicate_objects)

    def __remove_element_objects(self, predicate: Predicate, predicate_objects):
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
            self.__adjust_index_remove_element(predicate.name, i)

    def __remove_element_no_objects(self, predicate: Predicate):
        """Params:  - predicate : Predicate"""
        index = self.get_indexes(predicate.name)
        assert len(index) == 1
        index = index[0]

        # Do the deletion
        del self.elements[index]

        # Adjust self._index
        self.__adjust_index_remove_element(predicate.name, index)

    def __adjust_index_remove_element(self, identifier: str, index_removed: int):
        assert type(identifier) == str and type(index_removed) == int
        # Remove deleted element from self._index
        if len(self._index[identifier]) == 1:
            del self._index[identifier]
        else:
            del self._index[identifier][self._index[identifier].index(index_removed)]

        # Update self._index
        for k in self._index.keys():
            i = 0
            while i < len(self._index[k]):
                if self._index[k][i] > index_removed:
                    self._index[k][i] -= 1
                i += 1

    def check_if_predicate_value_exists(self, predicate: Predicate, obs: list) -> bool:
        indexes = self.get_indexes(predicate.name)
        prob_pred = ProblemPredicate(predicate, obs)
        if indexes is None:
            return False
        for i in indexes:
            if self.elements[i] == prob_pred:
                return True
        return False

    @staticmethod
    def reproduce(state):
        returnState = State()
        for e in state.elements:
            returnState.add_element(e)
        return returnState

    @staticmethod
    def compare_states(state1, state2):
        """:returns - True if state1 and state2 are equal
        :returns    - False otherwise"""
        # Check lengths
        if len(state1) != len(state2):
            return False

        # Check state contents
        for e in state1.elements:
            validated = False
            for i in state2.elements:
                if e.predicate == i.predicate and e.objects == i.objects:
                    validated = True
                    break
            if not validated:
                return False
        return True

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if len(self.elements) != len(other.elements):
            return False
        for el in self.elements:
            if el not in other.elements:
                return False
        return True

    def __len__(self):
        return len(self.elements)

    def __str__(self):
        if len(self.elements) > 0:
            print_string = ""
            for e in self.elements[:-1]:
                print_string += str(e) + "\n"
            print_string += str(self.elements[-1])
        else:
            print_string = "State is empty."
        return print_string
