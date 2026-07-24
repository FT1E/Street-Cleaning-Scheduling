
from data.read_data import get_graph_demanded_edges, get_vehicle_data, get_graph_al, get_graph_edge_list
from algorithms.greedy_single import run as gs_run
from algorithms.greedy_dynamic_cluster import run as gdc_run
from algorithms.greedy_fixed_cluster import run as gfc_run

from solution_representation.Solution import Solution


from algorithms.local_search_first_found import run as ls_run

import copy
import time

GRAPH_ID = 0
VEHICLE_ID = 0


# todo - remove demanded edges with frequency higher than planning period, or just make them zero-demand edges

vehicle = get_vehicle_data(VEHICLE_ID)

# ! below for debugging
# vehicle['distance_limit'] = 500     
# print(f"Vehicle distance limit: {vehicle['distance_limit']}")
# vehicle['planning_duration'] = 7
vehicle['count'] = 50           # ? playing around with this value so it's not too high, but also not too low so some edges don't get serviced at all
# (graph_id, vehicle_id) >= value so that no edge is ignored (not serviced at all)
# (0, 0) >= 33



demanded_edges = get_graph_demanded_edges(GRAPH_ID, filter = vehicle['planning_duration'])
adjacency_list = get_graph_al(GRAPH_ID)


# print(vehicle)
# day_assignments, capacity_used = gs_run(demanded_edges, vehicle)
day_assignments, capacity_used =    gdc_run(demanded_edges, adjacency_list, vehicle)
# day_assignments, capacity_used = gfc_run(demanded_edges, adjacency_list, vehicle, GRAPH_ID)



solution = Solution(day_assignments, demanded_edges, adjacency_list, vehicle, GRAPH_ID)

# print('Printing solution ...')
# print(solution)

eval_start_t = time.time()
cost = solution.evaluate()
eval_end_t = time.time()

eval_time = eval_end_t - eval_start_t

print(f"Solution cost: {cost}")

unsatisfied_edges = solution.unsatisfied_edges()

print(f"Number of all demanded edges: {len(demanded_edges)}")
print(f"Number of unsatisfied edges: {len(unsatisfied_edges)}")

# for edge in unsatisfied_edges:
#     print(edge)
#     print(f'\t{edge.service_days}')


print(f"Expected number of total services: {solution.expected_number_of_services()}")
print(f"Actual number of total services: {solution.total_number_of_services()}")


# solution.checking_references()

# ls_run(solution)

from algorithms.local_search import op1, undo_op1
from algorithms.local_search import op2, undo_op2
from algorithms.local_search import op3, undo_op3
from algorithms.local_search import op4, undo_op4
from algorithms.local_search import op5, undo_op5
from algorithms.local_search import op6, undo_op6
from algorithms.local_search import op7, undo_op7
import random
print(f"\n\nTime it took for 1 evaluate: {eval_time} seconds")

edge = random.choice(solution.demanded_edges)
day_1 = random.choice(edge.service_days)
no_service_days = (set(solution.get_work_days())).difference(edge.service_days)
day_2 = random.choice(list(no_service_days))

start_time = time.time()
route, route_pos = op1(solution, day_1, day_2, edge)
end_time = time.time()
op1_time = end_time - start_time

start_time = time.time()
undo_op1(solution, day_1, day_2, edge, route, route_pos)
end_time = time.time()

undo_op1_time = end_time - start_time


edge_1, edge_2 = random.sample(solution.frequency_buckets[7], 2)

if edge_1 is None:
    print("Random sample on freq buckets not working")

start_time = time.time()
op2(solution, edge_1, edge_2)
end_time = time.time()

op2_time = end_time - start_time

start_time = time.time()
undo_op2(solution, edge_1, edge_2)
end_time = time.time()

undo_op2_time = end_time - start_time


start_time = time.time()
route, route_pos = op6(solution, day_1, edge)
end_time = time.time()

op6_time = end_time - start_time


start_time = time.time()
undo_op6(solution, day_1, edge, route, route_pos)
end_time = time.time()

undo_op6_time = end_time - start_time


start_time = time.time()
op7(solution, day_2, edge)
end_time = time.time()

op7_time = end_time - start_time


start_time = time.time()
undo_op7(solution, day_1, edge)
end_time = time.time()

undo_op7_time = end_time - start_time

day_1 = day_1


route_1, route_2 = random.sample(solution.days[day_1].routes, 2)

while len(route_1.targets) <= 1:
    route_1, route_2 = random.sample(solution.days[day_1].routes, 2)

r1_cutpoint = random.randint(0, len(route_1.targets) - 2)
r2_cutpoint = random.randint(0, len(route_2.targets) - 1)


start_time = time.time()
res = op3(solution, route_1, route_2, r1_cutpoint, r2_cutpoint)
end_time = time.time()

op3_time = end_time - start_time

delta_cost, route_1_undo, route_2_undo, cnt = res

start_time = time.time()
undo_op3(solution, route_1_undo, route_2_undo, cnt)
end_time = time.time()

undo_op3_time = end_time - start_time

start_time = time.time()
op4(solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
end_time = time.time()

op4_time = end_time - start_time

start_time = time.time()
undo_op4(solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
end_time = time.time()

undo_op4_time = end_time - start_time


start_time = time.time()
op5(solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
end_time = time.time()

op5_time = end_time - start_time


start_time = time.time()
undo_op5(solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
end_time = time.time()

undo_op5_time = end_time - start_time



print("Time it took for a single performance of each operation")
print(f"\nop1 Time:\t {op1_time:.10f} seconds")
print(f"undo_op1 Time:\t {undo_op1_time:.10f} seconds")
print(f"\nop2 Time:\t {op2_time:.10f} seconds")
print(f"undo_op2 Time:\t {undo_op2_time:.10f} seconds")
print(f"\nop3 Time:\t {op3_time:.10f} seconds")
print(f"undo_op3 Time:\t {undo_op3_time:.10f} seconds")
print(f"\nop4 Time:\t {op4_time:.10f} seconds")
print(f"undo_op4 Time:\t {undo_op4_time:.10f} seconds")
print(f"\nop5 Time:\t {op5_time:.10f} seconds")
print(f"undo_op5 Time:\t {undo_op5_time:.10f} seconds")
print(f"\nop6 Time:\t {op6_time:.10f} seconds")
print(f"undo_op6 Time:\t {undo_op6_time:.10f} seconds")
print(f"\nop7 Time:\t {op7_time:.10f} seconds")
print(f"undo_op7 Time:\t {undo_op7_time:.10f} seconds")
