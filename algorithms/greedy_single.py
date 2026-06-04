

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
vehicle = get_vehicle_data(GRAPH_ID)

# print(vehicle)

# todo - for now just assigning edges according to priority
# todo - limited by [sum of edge demand for any day i] < [vehicle capacity]


# todo - limited by [sum of routing cost for any day i] < [vehicle distance_limit]
# * need to do a bit more for this


day_assignment = [[] for _ in range(vehicle['planning_duration'])]
capacity_used = [0] * vehicle['planning_duration']

next_day_streets = []

# todo - replace 7 with vehicle['planning_duration']
for day in range(vehicle['planning_duration']):

    if day in vehicle['days_no_service']:
        # skip day if vehicle not available for today
        continue

    edges = list(hq.merge(edges, next_day_streets))

    next_day_streets = []

    while capacity_used[day] < vehicle['capacity'] and len(edges) > 0:
        
        # get edge with nearest deadline
        edge = hq.heappop(edges)

        if capacity_used[day] + edge.demand > vehicle['capacity']:
            # if edge has higher demand than the vehicle can handle for the day then skip it for today
            hq.heappush(next_day_streets, edge)
            continue

        capacity_used[day] += edge.demand
        day_assignment[day].append(edge)
        edge.set_cleaning_day(day)


        if (edge.last_cleaning_day + edge.freq) < vehicle['planning_duration']:
            hq.heappush(next_day_streets, edge)

# todo - should I calculate routing cost when I assign every new single edge?

print(f"Max vehicle capacity: {vehicle['capacity']}")
for i in range(vehicle['planning_duration']):
    if len(day_assignment[i]) > 0:
        print(f"Edges Assigned for day {i}:")
        for e in day_assignment[i]:
            print(e.number, end=', ')
        print(f"\nCapacity used for day {i}:{str(capacity_used[i])}")
        routing_cost = calculate_cost(adjacency_list, day_assignment[i], vehicle)
        # since the same graph is used - distances should be calculated only once
        vehicle['distance_limit'] = 160     # ! for debugging purposes
        print(f"Routing cost info for day {i}:{routing_cost['total_distance']}\nNumber of routes: {routing_cost['num_routes']}\n\nRoutes")
        for route in routing_cost['routes']:
            print(route.targets)
        print('\n-----------------------------\n')