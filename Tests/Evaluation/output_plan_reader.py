import argparse
import os.path, os
import sys
import pickle

original_path = os.getcwd()
try:
    from Solver.Models.model import Model
    from Solver.Solving_Algorithms.solver import Solver
except:
    os.chdir("../..")
    sys.path.insert(1, os.getcwd())
    from Solver.Models.model import Model
    from Solver.Solving_Algorithms.solver import Solver
    os.chdir(original_path)

"""Plans can be output and stored as pickle objects. This file opens the file and prints the contents"""


def read_plan(result_file_path: str) -> Model:
    # Check file exists
    if not os.path.exists(result_file_path):
        raise IOError("File {} could not be found".format(result_file_path))
    with (open(result_file_path, "rb")) as openfile:
        model = pickle.load(openfile)
    return model


def display_plan(res):
    Solver.output(res)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(exit_on_error=False)
    argparser.add_argument("FilePath", metavar='FP', type=str, nargs="?", help='File path to Pickled Result File',
                           default=None)
    argparser.format_help()
    args = argparser.parse_args()

    file_path = args.FilePath
    result = read_plan(file_path)
    display_plan(result)
