import cProfile
import pstats
import io
import time
from runner import Runner
from Solver.Solving_Algorithms.partial_order_novelty import PartialOrderNoveltySolver
from Solver.Solving_Algorithms.partial_order_novelty_methods import PartialOrderNoveltyMethodsSolver
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
from Solver.Heuristics.landmarks import Landmarks
from Solver.Heuristics.hamming_distance_seen_states import HammingDistanceSeenStatesPruning
from Solver.Heuristics.tree_distance_seen_states import TreeDistanceSeenStatesPruning
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue
from Solver.Search_Queues.Novelty_GBFS_Search_Queue import NoveltyGBFSQueue
from Solver.Search_Queues.Greedy_Cost_So_Far_Search_Queue import GreedyCostSearchQueue

domain_file_path = "Tests/Examples/Rover/domain.hddl"
problem_file_path = "Tests/Examples/Rover/p08.hddl"
pr = cProfile.Profile()
pr.enable()
controller = Runner(domain_file_path, problem_file_path)

###########################################################
# controller.set_search_queue(GBFSSearchQueue)
# controller.set_heuristic(HammingDistancePartialOrder)
###########################################################
controller.set_search_queue(GBFSSearchQueue)
# controller.set_search_queue(GreedyCostSearchQueue)
controller.set_heuristic(Landmarks)
###########################################################
# controller.set_solver(PartialOrderNoveltySolver)
# controller.set_search_queue(NoveltyGBFSQueue)
###########################################################
# controller.set_search_queue(GBFSSearchQueue)
# controller.set_heuristic(TreeDistanceSeenStatesPruning)
###########################################################
# controller.set_solver(PartialOrderNoveltyMethodsSolver)
# controller.set_search_queue(NoveltyGBFSQueue)
###########################################################

controller.parse_domain()
controller.parse_problem()
controller.solver.solve(search=False)
start_time = time.time()
res = None
print('Ready to Begin Solving!')
while time.time() - start_time < 150 and not res:  # while time.time() - start_time < 305
    res = controller.solver._search(True)
pr.disable()

result = io.StringIO()
pstats.Stats(pr, stream=result).print_stats()
result = result.getvalue()
# chop the string into a csv-like buffer
result = 'ncalls' + result.split('ncalls')[-1]
result = '\n'.join([','.join(line.rstrip().split(None, 5)) for line in result.split('\n')])
# save it to disk

with open('output/runner-landmarks-profile8Rover8WithDeleteRelaxed3.csv', 'w+') as f:
    # f=open(result.rsplit('.')[0]+'.csv','w')
    f.write(result)
    f.close()
controller.output_result(res)
