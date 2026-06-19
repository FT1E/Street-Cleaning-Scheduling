
from data.read_data import get_graph_demanded_edges, get_vehicle_data, get_graph_al
from algorithms.greedy_fixed_cluster import run as gfc_run
from util.logger import print_day_assignment

GRAPH_ID = 8
VEHICLE_ID = 6

demanded_edges = get_graph_demanded_edges(GRAPH_ID)
adjacency_list = get_graph_al(GRAPH_ID)
vehicle = get_vehicle_data(VEHICLE_ID)

vehicle['distance_limit'] = 500     # ! for debugging


day_assignment, capacity_used = gfc_run(demanded_edges, adjacency_list, vehicle)


print('\nStatic Clusters result:')
print('-'*100)
print('-'*100)
print('\n')


print_day_assignment(day_assignment, adjacency_list, vehicle, capacity_used=capacity_used)