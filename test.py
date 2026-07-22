
from data.read_data import get_graph_demanded_edges, get_vehicle_data, get_graph_al, get_graph_edge_list
from algorithms.greedy_single import run as gs_run
from algorithms.greedy_dynamic_cluster import run as gdc_run
from algorithms.greedy_fixed_cluster import run as gfc_run

from solution_representation.Solution import Solution


from algorithms.local_search import run as ls_run

import copy

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

cost = solution.evaluate()
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

ls_run(solution)