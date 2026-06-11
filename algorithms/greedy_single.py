

import sys
import heapq as hq

sys.path.append('..')
from data.read_data import get_graph_demanded_edges, get_vehicle_data, get_graph_al, PriorityType
from util.routing_heuristic import calculate_cost

# todo - set values for below with cmd args if given
GRAPH_ID = 8
VEHICLE_ID = 6

edges = get_graph_demanded_edges(GRAPH_ID)

# below used for calculating routing cost
adjacency_list = get_graph_al(GRAPH_ID, PriorityType.Distance)

hq.heapify(edges)

# get vehicle data
vehicle = get_vehicle_data(VEHICLE_ID)

# print(vehicle)


day_assignment = [[] for _ in range(vehicle['planning_duration'])]
capacity_used = [0] * vehicle['planning_duration']

next_day_streets = [[] for _ in range(vehicle['planning_duration'] + 1)]


for day in range(vehicle['planning_duration']):

    if day in vehicle['days_no_service']:
        # skip day if vehicle not available for today
        continue

    edges = list(hq.merge(edges, next_day_streets[0]))


    for i in range(vehicle['planning_duration'] - day - 1):
        next_day_streets[i] = next_day_streets[i+1]
        

    while capacity_used[day] < vehicle['capacity'] and len(edges) > 0:
        
        # get edge with nearest deadline
        edge = hq.heappop(edges)

        if capacity_used[day] + edge.demand > vehicle['capacity']:
            # if edge has higher demand than the vehicle can handle for the day then skip it for today
            hq.heappush(next_day_streets[0], edge)
            continue

        capacity_used[day] += edge.demand
        day_assignment[day].append(edge)
        edge.set_cleaning_day(day)


        if (edge.last_cleaning_day + edge.freq) < vehicle['planning_duration']:
            # push it to the future for at least freq/2 days
            # so some edgees that have higher frequency aren't clean
            hq.heappush(next_day_streets[int(edge.freq // 2)], edge)


vehicle['distance_limit'] = 500     # ! for debugging purposes

print(f"Max vehicle capacity: {vehicle['capacity']}")

total_distance = 0

day_routing_info = []

for i in range(vehicle['planning_duration']):
    if len(day_assignment[i]) > 0:
        print(f"Edges Assigned for day {i}:")
        for e in day_assignment[i]:
            print(e.number, end=', ')
        print(f"\nCapacity used for day {i}:{str(capacity_used[i])}")
        routing_cost = calculate_cost(adjacency_list, day_assignment[i], vehicle)
        # since the same graph is used - distances should be calculated only once
        print(f"Total routing distance for day {i}:{routing_cost['total_distance']}\nNumber of routes: {routing_cost['num_routes']}\n\nRoutes")
        for route in routing_cost['routes']:
            print(f'Route length: {route.length}')
            print(route.targets)
        print('\n-----------------------------\n')
        total_distance += routing_cost['total_distance']

        day_routing_info.append(routing_cost)

print(f"\nTotal distance for all days: {total_distance}")

# output saved in 
# (day_assignment, day_routing_info)
# day_routing_info can be calculated from day_assignment