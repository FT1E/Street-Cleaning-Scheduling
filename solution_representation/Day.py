
import sys
import random

sys.path.append('..')

from util.routing_heuristic import calculate_cost
from solution_representation.Route import Route

# used in the solution representation to represent a single day of the solution consisting of routes in the day
# also has a list of edges, which can be inferred from the routes

# todo - note when to change day.total_distance


class Day:

    def __init__(self, number, serviced_edges, adjacency_lists, vehicle, graph_id):
        
        self.number = number

        # ? below 2 are just for reference
        self.adjacency_lists = adjacency_lists
        self.vehicle = vehicle
        self.graph_id = graph_id

        self.edges = serviced_edges

        self.recalculate_routes()

    # - edge is added in a random route at the end
    # - or the route and position can be specified - for undo operations
    def add_edge(self, edge, route=None, pos=None):

        if not self.add_edge_in_list(edge):
            print(f"\n{edge} already added in day {self.number}\n")


        # if a specific route is given - insert it in it and finish
        # this is for undo
        if route is not None:
            route.insert_edge(edge, pos = pos)
            if len(route.targets) == 1:
                self.add_route(route)
            return


        # else either make a new route if day has no routes, or insert it in a random one
        if len(self.routes) == 0:
            # if day has no routes
            route = Route([edge], day = self)
            self.add_route(route)
        else:
            # add it to a random route
            # other operators will move it to a better route
            random.choice(self.routes).insert_edge(edge)
            
    
    # after removing an edge, remove it in the route which it was contained
    # the return result is the removed edge if it was serviced in this day, otherwise None
    def remove_edge(self, edge=None):

        # in the route containing that edge just remove it and recalculate the cost and demand
        # implicitly connect the points which were connected by the removing edge
        # ex. say remove b in 0-a-b-c-0, result is 0-a-c-0, where 0 is depot node

        affected_route = self.get_edge_route(edge)

        if affected_route is None:
            print(f"\nTrying to remove {edge} from day {self.number} (day number) but its route not present\n")
            # raise Exception()
            return

        self.remove_edge_in_list(edge)
        affected_route.remove_edge(edge)

        if len(affected_route.targets) == 0:
            self.remove_route(affected_route)

        # below done in above
        # if len(affected_route.targets) == 1:
        #     self.routes.append(affected_route)
        
        return edge

    def recalculate_routes(self):
        
        info = calculate_cost(self.adjacency_lists, self.edges, self.vehicle, self.graph_id)

        self.total_distance = info['total_distance']
        self.routes = info['routes']

        for route in self.routes:
            route.set_day(self)

    def calculate_total_distance(self):
        self.total_distance = 0
        for route in self.routes.copy():
            if len(route.targets) == 0:
                self.routes.remove(route)
                continue
            self.total_distance += route.length
        return self.total_distance

    def __repr__(self):
        self.print()
        return ""
    
    def print(self):
        print(f"Day {self.number}:")
        print(f"\tNumber of edges: {len(self.edges)}")
        for edge in self.edges:
            print(f"\t{edge}")
        print(f"\tNumber of routes: {len(self.routes)}")
        cnt = 1
        for route in self.routes:
            print(f"\tRoute {cnt}")
            route.print()
            cnt += 1

    def remove_route(self, route=None, route_id=None):
        if route is not None:
            try:
                self.routes.remove(route)
            except:
                print(f"\nFailed to remove route in day {self.number} given as value\n")
                pass
                raise Exception()
        elif route_id is not None:
            try:
                route = self.routes.pop(route_id)
            except:
                print(f"\nFailed to remove route in day {self.number} given as route_id\n")
                pass
                raise Exception()

    def add_route(self, route):
        if len(route.targets) > 0 and route not in self.routes:
            self.routes.append(route)
            route.set_day(self)
            return True
        return False

    def add_edge_in_list(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)
            return True
        return False

    def remove_edge_in_list(self, edge):
        try:
            self.edges.remove(edge)
        except:
            print(f"\nTrying to remove {edge} for edge list but not in it for day {self.number} (day number)\n")
            pass

    def get_edge_route(self, edge):
        for route in self.routes:
            if edge in route.targets:
                return route

        if edge in self.edges:
            print(f"\n{edge} in day {self.number} (day number) but no route in it\n")
        return None

    def edge_in_day(self, edge):
        if edge not in self.edges:
            # print(f"{edge} not in day {self.number} edge list")
            return False
        if self.get_edge_route(edge) is None:
            print(f"\n{edge} in day {self.number} list, but in no route inside\n")
            return False

        return True