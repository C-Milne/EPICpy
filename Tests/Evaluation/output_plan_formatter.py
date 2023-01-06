import pickle
import os
import sys


original_path = os.getcwd()
try:
    from Solver.Models.model import Model
    from Solver.Solving_Algorithms.solver import Solver
    from Solver.Progress_Tracking.action_tracker import ActionTracker
except:
    os.chdir("../..")
    sys.path.insert(1, os.getcwd())
    from Solver.Models.model import Model
    from Solver.Solving_Algorithms.solver import Solver
    from Solver.Progress_Tracking.action_tracker import ActionTracker
    os.chdir(original_path)


def format_output(pickle_plan_file_path):
    with (open(pickle_plan_file_path, "rb")) as openfile:
        model = pickle.load(openfile)
    for m in model:
        print(m)


if __name__ == "__main__":
    format_output("Heuristic_Evaluation/Archive/Rover/serialised_objects/Rover_p01hddl_Breadth_First_Operations_actions.pickle")