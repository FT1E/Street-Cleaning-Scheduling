

import heapq as hq


CLUSTER_LIMIT = 5   # TODO - play with numbers, also consider case of infinite - like selecting 1 edge, then building assignment for day from it / around it


# ? method returns assignment of edges
def run(demanded_edge_list, adjacency_lists, vehicle, CLUSTER_LIMIT = 5):
    
    
    day_assignment = [[] for _ in range(vehicle['planning_duration'])]
    
    
    # ? below not needed - just for caching
    capacity_used = [0] * vehicle['planning_duration']


    # ? below is if an edge needs to be served multiple times
    next_day_streets = [[] for _ in range(vehicle['planning_duration'] + 1)]
    
    
    # ? info for dynamic cluster 
    cluster_heap = []
    current_cluster_size = 0
    cluster_vertices = []

    cluster_edges = []
    cluster_origin = None

    # going through every day
    # during this loop edges are only assigned to days
    # routes are formed after that with Clarke-Wright heuristic
    for day in range(vehicle['planning_duration']):

        if day+1 in vehicle['days_no_service']:
            # skip day if vehicle not available for today
            continue

        # adding edges which need to be serviced
        #   - either previously serviced
        #   - or vehicle couldn't service due to capacity limitations
        demanded_edge_list = list(hq.merge(demanded_edge_list, next_day_streets[0]))
        for i in range(vehicle['planning_duration'] - day - 1):
            next_day_streets[i] = next_day_streets[i+1]



        while capacity_used[day] < (vehicle['count'] - 2)* vehicle['capacity'] and len(demanded_edge_list) > 0:

            # get edge with nearest deadline
            edge = hq.heappop(demanded_edge_list)

            # add it to cluster_heap
            hq.heappush(cluster_heap, edge)

            # ? reseting to default values for dynamic cluster
            current_cluster_size = 0
            cluster_vertices = []
            cluster_edges = []
            cluster_origin = edge
            
            # ? loop for expanding cluster until vehicle limit
            # ? CLUSTER_LIMIT = maximum number of edges allowed in the cluster (possibly infinite)
            while current_cluster_size < CLUSTER_LIMIT and len(cluster_heap) > 0:

                # get top priority edge from cluster heap
                edge = hq.heappop(cluster_heap)

                # if edge is already assigned to this day
                if edge in day_assignment[day]:
                    # print(f"Edge {edge} is already assigned to day {day}")
                    continue

                # if edge doesn't require cleaning
                if edge.demand <= 0:

                    # if len(cluster_heap) == 0 and current_cluster_size == 1:
                    #     # print(f"Top edge was surrounded by edges with zero demand")
                    #     pass
                    # ? if top edge has non-positive demand then all further ones have as well 
                    break

                if capacity_used[day] + edge.demand > vehicle['count'] * vehicle['capacity']:
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
            
    return day_assignment, capacity_used