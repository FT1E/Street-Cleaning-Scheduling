import heapq as hq
import math

memo_distances = None
# todo - use a bit of memoization, since I'm using the same graph
# todo - it's enough to calculate the distances once between every pair of vertices/nodes

# todo - also consider how number of vehicles limits the routing 


def calculate_distances(adjacency_list):
    global memo_distances

    # ? for debugging purposes - seeing the graph's max distance
    max_distance = 0

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
                
                if min_edge.distance > max_distance:
                    max_distance = min_edge.distance

                for edge in adjacency_list[min_edge.end_node]:
                    hq.heappush(current, edge)

    # print(f"Max distance in the graph: {max_distance}")

def get_min_distances(adjacency_list=None):
    global memo_distances

    if adjacency_list is not None:
        calculate_distances(adjacency_list)
    
    return memo_distances
    
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
    
    def internal_targets(self):
        # check if both targets are either beginning or ending points of the route
        route = self.target_1.route
        pos_in_route = route.targets.index(self.target_1)
        if pos_in_route > 0 and pos_in_route < len(route.targets) - 1:
            return True
        
        # same for target 2
        route = self.target_2.route
        pos_in_route = route.targets.index(self.target_2)
        if pos_in_route > 0 and pos_in_route < len(route.targets) - 1:
            return True
        
   


class Route:
    def __init__(self, targets, length=-1, demand=-1):
        self.targets = targets

        if length == -1:
            self.length = min_distance_ne(0, targets[0]) + min_distance_ne(0, targets[-1])
            for i in range(len(targets) - 1):
                self.length += min_distance_ee(targets[i], targets[i+1])
        else:
            self.length = length

        if demand == -1:
            self.demand = 0
            for target in targets:
                self.demand += target.demand
        else:
            self.demand = demand

    def merge(self, other, saving):
        # todo - merge two routes and calculate the new length
        
        t1 = saving.target_1
        if t1 not in self.targets:
            t1 = saving.target_2
            t2 = saving.target_1
        else:
            t2 = saving.target_2

        if self.targets.index(t1) == 0:
            self.targets.reverse()

        if other.targets.index(t2) == 0:
            new_targets = self.targets + other.targets
        else:
            new_targets = other.targets + self.targets
        
        length = self.length + other.length - saving.saving
        return Route(new_targets, length, self.demand + other.demand)

    def set_target_routes(self):
        for target in self.targets:
            target.route = self

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

    # ! ASSUMING NODE 0 IS THE DEPOT
    # initial routing depot-target-depot
    for i in range(len(targets)):
        routes.append(Route([targets[i]]))
        distance = 2 * min_distance_ne(0, targets[i])
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
        
        if top_saving.saving <= 0:
            break      # if the top saving has a negative value stop and return the routes made so far
        
        if top_saving.same_route():
            continue    # if this link is in the same route

        if top_saving.internal_targets():
            continue    # if one of the targets is a mid-point in a route (not beginning or ending point)


        # check if vehicle can handle the distance and capacity of the merged route
        route_1 = top_saving.target_1.route
        route_2 = top_saving.target_2.route

        new_route = route_1.merge(route_2, top_saving)

        if new_route.length > vehicle['distance_limit']:
            continue
        if new_route.demand > vehicle['capacity']:
            continue

        # else it's fine and merge the routes
        routes.remove(route_1)
        routes.remove(route_2)

        routes.append(new_route)
        new_route.set_target_routes()


    # organize the output
    res = {'total_distance' : 0, 'num_routes' : len(routes), 'routes' : routes}
    # ! having num_routes since 1 vehicle could in theory take multiple routes given enough capacity and distance
    # todo - consider above - another optimization problem - which routes which vehicle takes

    # calculate distance covered
    for route in routes:
        res['total_distance'] += route.length

    return res
