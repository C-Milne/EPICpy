import cProfile
import pstats
import io
from runner import Runner
from Solver.Heuristics.hamming_distance_partial_order import HammingDistancePartialOrder
from Solver.Search_Queues.Greedy_Best_First_Search_Queue import GBFSSearchQueue

domain_file_path = "Tests/Examples/Rover/domain.hddl"
problem_file_path = "Tests/Examples/Rover/p08.hddl"
pr = cProfile.Profile()
pr.enable()
controller = Runner(domain_file_path, problem_file_path)
controller.set_search_queue(GBFSSearchQueue)
controller.set_heuristic(HammingDistancePartialOrder)
controller.parse_domain()
controller.parse_problem()
controller.solver.solve()
pr.disable()

result = io.StringIO()
pstats.Stats(pr, stream=result).print_stats()
result = result.getvalue()
# chop the string into a csv-like buffer
result = 'ncalls' + result.split('ncalls')[-1]
result = '\n'.join([','.join(line.rstrip().split(None, 5)) for line in result.split('\n')])
# save it to disk

with open('output/runner-profile.csv', 'w+') as f:
    # f=open(result.rsplit('.')[0]+'.csv','w')
    f.write(result)
    f.close()
