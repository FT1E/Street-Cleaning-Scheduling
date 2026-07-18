
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
    def frequency_satisfied(self):
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

                if t2 - t1 > edge.freq:
                    unsatisfied_edges.append(edge)
                    break   # out of inner loop and continue with next edge in outer loop
        
        print(f"{ignored_edges} edges were not serviced at all!")

        return unsatisfied_edges, ignored_edges, 

    # todo - operators for getting a neigbouring solution

class Day:

    def __init__(self, number, edges, adjacency_lists, vehicle, graph_id):
        
        self.number = number

        # ? below 2 are just for reference
        self.adjacency_lists = adjacency_lists
        self.vehicle = vehicle
        
        self.edges = edges

        info = calculate_cost(self.adjacency_lists, edges, self.vehicle, graph_id)

        self.total_distance = info['total_distance']
        self.routes = info['routes']
        self.route_count = len(self.routes)


# ? note that there is a class Route in read_data, defined there since it's also used there for Clarke-Wright heuristic
