
import sys

sys.path.append('..')

from util.routing_heuristic import calculate_cost

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

    # after adding an edge, routes for the day are recalculated
    # todo - could try appending the edge either at a beginning or end of a route
    def add_edge(self, edge, recalculate=True):
        self.edges.append(edge)
        if recalculate:
            self.recalculate_routes()
    
    # after removing an edge, remove it in the route which it was contained
    # the return result is the removed edge if it was serviced in this day, otherwise None
    def remove_edge(self, edge=None, edge_id=None, recalculate=False):
        # remove it from list of edges
        try:
            if edge is not None:
                self.edges.remove(edge)
            elif edge_id is not None:
                edge = self.edges.pop(edge_id)
            else:
                return None
        except:
            # in case edge is not serviced in this day
            return None
        
        if recalculate:
            self.recalculate_routes()
            return

        # in the route containing that edge just remove it and recalculate the cost and demand
        # implicitly connect the points which were connected by the removing edge
        # ex. say remove b in 0-a-b-c-0, result is 0-a-c-0, where 0 is depot node

        affected_route = self.get_edge_route(edge)

        affected_route.remove_edge(edge)
                
        # if the edge was the only target in the route remove it
        if len(affected_route.targets) == 0:
            try:
                self.routes.remove(affected_route)
            except:
                print("Below edge was removed but its route not in list")
                print(edge)
                print("List of all routes:")
                self.print()
        return edge

    def recalculate_routes(self):
        
        info = calculate_cost(self.adjacency_lists, self.edges, self.vehicle, self.graph_id)

        self.total_distance = info['total_distance']
        self.routes = info['routes']

        for route in self.routes:
            route.set_day(self)

        self.route_count = len(self.routes)

    def recalculate_total_distance(self):
        self.total_distance = 0
        for route in self.routes:
            self.total_distance += route.length
        return self.total_distance

    def __repr__(self):
        self.print()
        return ""
    
    def print(self):
        print(f"Day {self.number}:")
        print(f"Number of edges: {len(self.edges)}")
        for edge in self.edges:
            print(f"\t{edge}")
        print(f"Number of routes: {self.route_count}")
        cnt = 1
        for route in self.routes:
            print(f"Route {cnt}")
            route.print()
            cnt += 1

    def remove_route(self, route=None, route_id=None):
        try:
            self.routes.pop(route_id)
            self.total_distance -= route.length
        except:
            try:
                self.routes.remove(route)
                self.total_distance -= route.length
            except:
                pass

    def add_route(self, route):
        if len(route.targets) > 0:
            self.routes.append(route)
            self.total_distance += route.length
            route.set_day(self)
            return True
        return False

    def add_edge_in_list(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def remove_edge_in_list(self, edge):
        try:
            self.edges.remove(edge)
        except:
            pass

    def get_edge_route(self, edge):
        for route in self.routes:
            if edge in route.targets:
                return route
        
        return None