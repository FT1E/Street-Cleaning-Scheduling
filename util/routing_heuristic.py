import heapq as hq
import math

memo_distances = None
# todo - use a bit of memoization, since I'm using the same graph
# todo - it's enough to calculate the distances once between every pair of vertices/nodes

# todo - also consider how number of vehicles limits the routing 


def calculate_distances(adjacency_list):
    global memo_distances

    memo_distances = dict()
    for i in range(len(adjacency_list)):
        memo_distances[i] = dict()
        current = adjacency_list[i].copy()

        # do dijkstra - take edge with smallest distance - then add that new point
        hq.heapify(current)
        while len(current) > 0:
            min_edge = hq.heappop(current)
            if min_edge.end_node not in memo_distances[i] or min_edge.distance < memo_distances[i][min_edge.end_node]:
                memo_distances[i][min_edge.end_node] = min_edge.distance
                for edge in adjacency_list[min_edge.end_node]:
                    hq.heappush(current, edge)

# get the minimum distance from a node to an edge
def min_distance_ne(node, edge):
    return min(memo_distances[node][edge.start_node], memo_distances[node][edge.end_node])


# get the minimum distance from an edge to another edge
def min_distance_ee(edge1, edge2):
    d1 = memo_distances[edge1.start_node][edge2.start_node]
    d2 = memo_distances[edge1.start_node][edge2.end_node]
    d3 = memo_distances[edge1.end_node][edge2.start_node]
    d4 = memo_distances[edge1.end_node][edge2.end_node]
    return min([d1, d2, d3, d4])



class Saving:
    def __init__(self, target_1, target_2, saving):
        self.target_1 = target_1
        self.target_2 = target_2
        self.saving = saving

    def __lt__(self, other):
        return self.saving < other.saving
    
    def same_route(self):
        return self.target_1.route == self.target_2.route
    
    def internal_targets(self, routes):
        # check if both targets are either beginning or ending points of the route
        route = self.target_1.route
        pos_in_route = route.index(self.target_1)
        if pos_in_route > 0 and pos_in_route < len(route) - 1:
            return True
        
        # same for target 2
        route = self.target_2.route
        pos_in_route = route.index(self.target_2)
        if pos_in_route > 0 and pos_in_route < len(route) - 1:
            return True
        
    def add_merged_route(self, routes):
        # check if both targets are either beginning or ending points of the route
        route_1 = self.target_1.route
        pos_in_route = route_1.index(self.target_1)
        if pos_in_route == 0:
            route_1.reverse()
        
        # same for target 2
        route_2 = self.target_2.route
        pos_in_route = route_2.index(self.target_2)
        if pos_in_route == 0:
            new_route = route_1 + route_2
        else:
            new_route = route_2 + route_1
        routes.remove(route_1)
        routes.remove(route_2)
        
        routes.append(new_route)
        new_route_id = routes.index(new_route)
        for edge in new_route:
            edge.route = new_route



# * using memoization so distances in a graph are calculated once and then re-using
# * using additional argument in case I'm switching between graphs
def calculate_cost(adjacency_list, targets, vehicle, recalculate_distances = False):
    
    global memo_distances

    # todo - calculate distances if None or using a different graph
    if memo_distances is None or recalculate_distances:
        calculate_distances(adjacency_list)


    # todo - routing heuristic, using the given points
    savings = []
    routes = []
    route_distance = []
    route_demand = []

    # ! ASSUMING NODE 0 IS THE DEPOT
    # initial routing depot-target-depot
    for i in range(len(targets)):
        routes.append([targets[i]])
        distance = 2 * min_distance_ne(0, targets[i])
        route_distance.append(distance)
        route_demand.append(targets[i].demand)
        targets[i].route = routes[i]
        

    # todo - modified a bit so that the targets are edges instead of single points
    # todo - so calculate the  distance = min (v1, v2) where v1, v2 are the nodes of the edge
    
    # todo - maybe organize the savings in a dictionary or a list with special objects with lt implemented

    for i in range(len(targets)):
        d0_e1 = min_distance_ne(0, targets[i])      # distance between depot and edge 1
        for j in range(i+1, len(targets)):
            d0_e2 = min_distance_ne(0, targets[j])              # distance between depot and edge 2
            d_e1_e2 = min_distance_ee(targets[i], targets[j])   # distance between edge 1 and edge 2

            saving = d0_e1 + d0_e2 - d_e1_e2             # savings by connecting edge 1 and edge 2

            savings.append(Saving(targets[i], targets[j], saving))

    hq.heapify(savings)
    while len(routes) > 1 and len(savings) > 1:
        
        top_saving = hq.heappop(savings)
        
        if top_saving.same_route():
            continue    # if this link is in the same route

        if top_saving.internal_targets(routes):
            continue    # if one of the targets is a mid-point in a route (not beginning or ending point)

        if top_saving.saving <= 0:
            break   # if the top saving has a negative value stop and return the routes made so far

        # check if vehicle can handle the distance and capacity of the merged route
        route_1 = top_saving.target_1.route
        route_2 = top_saving.target_2.route
        
        # distane between depot and first target + depot and last target
        r1_distance = min_distance_ne(0, route_1[0]) + min_distance_ne(0, route_1[-1])
        r2_distance = min_distance_ne(0, route_2[0]) + min_distance_ne(0, route_2[-1])
        
        # distance between mid-points
        for i in range(len(route_1) - 1):
            r1_distance += min_distance_ee(route_1[i], route_1[i+1])

        for i in range(len(route_2) - 1):
            r1_distance += min_distance_ee(route_2[i], route_2[i+1])
        
        new_route_distance = r1_distance + r2_distance - top_saving.saving

        if new_route_distance > vehicle['distance_limit']:
            continue

        new_route_demand = 0
        for target in route_1:
            new_route_demand += target.demand
        for target in route_2:
            new_route_demand += target.demand

        if new_route_demand > vehicle['capacity']:
            continue
        

        # else it's fine and merge the routes
        top_saving.add_merged_route(routes)

    # organize the output
    res = {'distance' : 0, 'num_routes' : len(routes), 'routes' : routes}
    # ! having num_routes since 1 vehicle could in theory take multiple routes given enough capacity and distance
    # todo - consider above - another optimization problem - which routes which vehicle takes

    # calculate distance covered
    for route in routes:
        # distances from depot to first node and last node to depot
        res['distance'] += min_distance_ne(0, route[0]) + min_distance_ne(0, route[-1])
        for i in range(len(route) - 1):
            res['distance'] += min_distance_ee(route[i], route[i+1])

    return res
