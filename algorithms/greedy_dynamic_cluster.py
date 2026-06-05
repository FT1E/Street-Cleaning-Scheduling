

import sys
import heapq as hq

sys.path.append('..')
from data.read_data import get_graph_al, get_graph_demanded_edges, get_vehicle_data, get_graph_metadata
from util.routing_heuristic import calculate_cost

GRAPH_ID = 8
VEHICLE_ID = 6
CLUSTER_LIMIT = 5   # TODO - play with numbers, also consider case of infinite - like selecting 1 edge, then building assignment for day from it / around it

# TODO - dictionary of key-value pairs
# TODO - in the heap only keep the keys (edge.number)

edges = get_graph_demanded_edges(GRAPH_ID)
# - adjacency lists for accessing adjacent edges faster/more easily
adjacency_lists = get_graph_al(GRAPH_ID)

hq.heapify(edges)

# get vehicle data
vehicle = get_vehicle_data(VEHICLE_ID)


# todo - assigning edges according to priority
# todo - limited by [sum of edge demand for any day i] < [vehicle capacity]


# - limited by vehicle distance_limit

graph_metadata = get_graph_metadata(GRAPH_ID)


day_assignment = [[] for _ in range(vehicle['planning_duration'])]
capacity_used = [0] * vehicle['planning_duration']

next_day_streets = [[] for _ in range(vehicle['planning_duration'] + 1)]
cluster_heap = []
current_cluster_size = 0
cluster_vertices = []

cluster_edges = []
cluster_origin = None

# vehicle['planning_duration'] = 7     # // ! for debugging purposes
    
for day in range(vehicle['planning_duration']):

    if day in vehicle['days_no_service']:
        # skip day if vehicle not available for today
        continue

    edges = list(hq.merge(edges, next_day_streets[0]))

    for i in range(vehicle['planning_duration'] - day - 1):
        next_day_streets[i] = next_day_streets[i+1]

    cluster_heap = []
    current_cluster_size = 0
    cluster_vertices = []
    cluster_origin = None

    while capacity_used[day] < vehicle['capacity'] and len(edges) > 0:

        # get edge with nearest deadline
        edge = hq.heappop(edges)

        # add it to cluster_heap
        hq.heappush(cluster_heap, edge)

        current_cluster_size = 0
        cluster_vertices = []
        cluster_edges = []
        cluster_origin = edge
        while current_cluster_size < CLUSTER_LIMIT and len(cluster_heap) > 0:

            # get priority edge from cluster heap
            edge = hq.heappop(cluster_heap)

            # if edge is already assigned to this day
            if edge in day_assignment[day]:
                # print(f"Edge {edge} is already assigned to day {day}")
                continue

            # if edge doesn't require cleaning
            if edge.demand <= 0:
                if len(cluster_heap) == 0 and current_cluster_size == 1:
                    # print(f"Top edge was surrounded by edges with zero demand")
                    pass
                continue

            if capacity_used[day] + edge.demand > vehicle['capacity']:
                # if edge has higher demand than the vehicle can handle for the day then skip it for today
                hq.heappush(next_day_streets[0], edge)
                continue

            # assign it to day
            capacity_used[day] += edge.demand
            day_assignment[day].append(edge)
            current_cluster_size += 1
            edge.set_cleaning_day(day)
            cluster_edges.append(edge)

            if (edge.last_cleaning_day + edge.freq) < vehicle['planning_duration']:
                hq.heappush(next_day_streets[int(edge.freq // 2)], edge)

            # - add new neighbouring edges to cluster heap
            # - keep track of which edges where added - which neighbourhoods of vertexes - basically just vertex number

            if edge.start_node not in cluster_vertices:
                cluster_vertices.append(edge.start_node)
                for adjacent_edge in adjacency_lists[edge.start_node]:
                    if adjacent_edge != edge:
                        hq.heappush(cluster_heap, adjacent_edge)            

            if edge.end_node not in cluster_vertices:
                cluster_vertices.append(edge.end_node)
                for adjacent_edge in adjacency_lists[edge.end_node]:
                    if adjacent_edge != edge:
                        hq.heappush(cluster_heap, adjacent_edge)
        
        if current_cluster_size > 0:
            # print(f"Cluster size: {current_cluster_size}, cluster origin: {cluster_origin}, cluster edges: {cluster_edges}")
            pass
        hq.heapify(edges)


vehicle['distance_limit'] = 500     # ! for debugging purposes

print(f"Max vehicle capacity: {vehicle['capacity']}")
total_distance = 0
for i in range(vehicle['planning_duration']):
    if len(day_assignment[i]) > 0:
        print(f"Edges Assigned for day {i}:")
        for e in day_assignment[i]:
            print(e, end=', ')
        print(f"\nCapacity used for day {i}:{str(capacity_used[i])}")
        
        
        routing_cost = calculate_cost(adjacency_lists, day_assignment[i], vehicle)

        print(f"Total routing distance for day {i}:{routing_cost['total_distance']}\nNumber of routes: {routing_cost['num_routes']}\n\nRoutes")
        for route in routing_cost['routes']:
            print(f'Route length: {route.length}')
            print(route.targets)
        print('\n-----------------------------\n')

        total_distance += routing_cost['total_distance']

print(f"\nTotal distance for all days: {total_distance}")