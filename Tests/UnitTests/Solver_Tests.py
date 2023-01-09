import unittest
from Solver.Models.default_model import DefaultModel
from Solver.Progress_Tracking.sequential_progress_tracker import SequentialTracker
from Solver.Progress_Tracking.action_tracker import ActionTracker
from Internal_Representation.state import State
from Internal_Representation.task import Task
from Tests.UnitTests.TestTools.env_setup import env_setup


class SolverTests(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_reproducing_model(self):
        domain, problem, parser, solver = env_setup(True)
        domain.add_task(Task('Task1'))

        old_progress_tracker = SequentialTracker()
        old_progress_tracker.add_operation(ActionTracker(domain.get_task('Task1'), {}))

        old_model = DefaultModel(State(), [], None, [], progress_tracker_class=SequentialTracker)
        old_model.set_progress_tracker(old_progress_tracker)

        new_model = solver.reproduce_model(old_model)

        self.assertEqual(new_model.current_state, old_model.current_state)
        self.assertEqual(new_model.model_number, 1)
        self.assertEqual(old_model.model_number, 0)
        self.assertEqual(new_model.progress_tracker, old_model.progress_tracker)

    def test_reproducing_model_adding_operations(self):
        domain, problem, parser, solver = env_setup(True)
        domain.add_task(Task('Task1'))
        domain.add_task(Task('Task2'))

        old_progress_tracker = SequentialTracker()
        old_progress_tracker.add_operation(ActionTracker(domain.get_task('Task1'), {}))

        old_model = DefaultModel(State(), [], None, [], progress_tracker_class=SequentialTracker)
        old_model.set_progress_tracker(old_progress_tracker)

        new_model = solver.reproduce_model(old_model)
        new_model.add_operation(domain.get_task('Task2'), {})

        new_model_operations_taken = SequentialTracker()
        new_model_operations_taken.add_operation(ActionTracker(domain.get_task('Task1'), {}))
        new_model_operations_taken.add_operation(ActionTracker(domain.get_task('Task2'), {}))

        old_model_operations_taken = SequentialTracker()
        old_model_operations_taken.add_operation(ActionTracker(domain.get_task('Task1'), {}))

        self.assertEqual(new_model.progress_tracker, new_model_operations_taken)
        self.assertEqual(old_model.progress_tracker, old_model_operations_taken)
        self.assertNotEqual(old_model.progress_tracker, new_model.progress_tracker)
