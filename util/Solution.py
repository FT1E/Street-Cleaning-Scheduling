
import sys
import math
sys.path.append('..')


from util.routing_heuristic import calculate_cost
from util.logger import print_day_assignment
from data.read_data import get_graph_al, get_vehicle_data



# class(es) for representing a solution
# performing changes on it
# evaluating how good it is

# Hierarchy
#   - each solution contains days
#   - each day contains trips routes for it
#   - each route contains a sequence of required edges to traverse

class Solution:

    # self.day_assignments[i] = routes for day i
    # self.work_day[i] = true if i is a work day, else false - depends on vehicle

    def __init__(self, day_assignments, demanded_edges, adjacency_lists, vehicle, graph_id):
        
        self.demanded_edges = demanded_edges

        self.arrays = day_assignments
        self.graph_id = graph_id
        self.days = []
        day_id = 1
        for day_assignment in day_assignments:
            self.days.append(Day(day_id, day_assignment, adjacency_lists, vehicle, graph_id))
            day_id += 1

        # ? below just for reference for calculating routing cost
        self.vehicle = vehicle
        self.adjacency_lists = adjacency_lists
        pass

    
    def __repr__(self):
        print_day_assignment(self.arrays, self.adjacency_lists, self.vehicle, self.graph_id)
        return ""

    def print(self):
        self.__repr__()

    # ! careful for out of bounds exceptions for below methods
    def get_day_routes(self, day):
        return self.day_assignments[day]

    def get_day_route_count(self, day):
        return len(self.day_assignments[day])

    def get_day_route(self, day, route):
        return self.day_assignments[day][route]


    # todo - calculates the cost for solution
    def evaluate(self):
        
        # vehicle count is the maximum number of vehicles used among all days, under the assumption that a vehicle has at most 1 route in a day
        # routing cost is the total routing cost among all day
        vehicle_count = 0
        routing_cost = 0
        for day in self.days:
            routing_cost += day.total_distance
            vehicle_count = max(vehicle_count, day.route_count)

        # todo - mix in vehicle count somehow, maybe as a weighted sum with a really high weight on vehicle count
        return routing_cost, vehicle_count

    # for checking if all edges had their frequency satisfied
    def unsatisfied_edges(self):
        # todo
        unsatisfied_edges = []
        ignored_edges = 0
        for edge in self.demanded_edges:
            if len(edge.service_days) == 0:
                ignored_edges += 1

            # expected_services = math.floor(self.vehicle['planning_duration'] / edge.freq)
            # if expected_services > len(edge.service_days):
            #     print(edge)
            #     print(f"\tExpected number of services: {expected_services}")
            #     print(f"\tActualnumber of services: {len(edge.service_days)}")
            #     print(f"\tService days: {edge.service_days}")


            for i in range(len(edge.service_days) - 1):
                t1 = edge.service_days[i]
                t2 = edge.service_days[i+1]

                max_spacing = math.ceil(edge.freq)
                if t2 - t1 > max_spacing:
                    unsatisfied_edges.append(edge)
                    break   # out of inner loop and continue with next edge in outer loop
        
        # print(f"{ignored_edges} edges were not serviced at all!")
        print(f"Number of unsatisfied edges: {len(unsatisfied_edges)}")
        return unsatisfied_edges 

    def get_work_days(self):
        # all except weekends - 5,6 - considering monday 0, tue 1, etc.
        return [i for i in range(len(self.days)) if i % 7 < 5]

    # todo - operators for getting a neigbouring solution

class Day:

    def __init__(self, number, edges, adjacency_lists, vehicle, graph_id):
        
        self.number = number

        # ? below 2 are just for reference
        self.adjacency_lists = adjacency_lists
        self.vehicle = vehicle
        self.graph_id = graph_id

        self.edges = edges

        self.recalculate_routes()

    # after adding an edge, routes for the day are recalculated
    # todo - could try appending the edge either at a beginning or end of a route
    def add_edge(self, edge, recalculate=True):
        self.edges.append(edge)
        if recalculate:
            self.recalculate_routes()
    
    # after removing an edge, remove it in the route which it was contained
    # the return result is the removed edge if it was serviced in this day, otherwise None
    def remove_edge(self, edge=None, edge_id=None):
        # remove it from list of edges
        try:
            if edge is not None:
                self.edges.remove(edge)
            elif edge_id is not None:
                edge = self.edges.pop(edge_id)
            else:
                return None
        except:
            return None
        
        # find the route which contains the edge
        affected_route = None
        for route in self.routes:
            if edge in route.targets:
                affected_route = route
                break
        if affected_route is None:
            return edge

        # once you find the route containing that edge just remove it and recalculate the cost and demand
        # implicitly connect the points which were connected by the removing edge
        # ex. say remove b in 0-a-b-c-0, result is 0-a-c-0
        # or 0-a-b-0, result is 0-a-0
        affected_route.targets.remove(edge)

        # if the edge was the only target in the route remove it
        if len(affected_route.targets) == 0:
            self.routes.remove(affected_route)
            return edge

        # otherwise recalculate route length and route demand
        affected_route.calculate_length()
        affected_route.calculate_demand()

        return edge

    def recalculate_routes(self):
        
        info = calculate_cost(self.adjacency_lists, self.edges, self.vehicle, self.graph_id)

        self.total_distance = info['total_distance']
        self.routes = info['routes']
        self.route_count = len(self.routes)

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

    def remove_route(self, route):
        try:
            self.routes.remove(route)
            self.total_distance -= route.length
        except:
            pass

    def add_route(self, route):
        self.routes.append(route)
        self.total_distance += route.length

# ? note that there is a class Route in read_data, defined there since it's also used there for Clarke-Wright heuristic
