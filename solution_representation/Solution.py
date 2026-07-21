
# used mainly in local search
# represents a solution which can be manipulated to get a different (neighbouring) solution

# class(es) for representing a solution
# performing changes on it
# evaluating how good it is

import sys
import math
sys.path.append('..')
from util.logger import print_day_assignment
from solution_representation.Day import Day

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


    # - calculates the cost for solution
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
                unsatisfied_edges.append(edge)

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
        # print(f"Number of unsatisfied edges: {len(unsatisfied_edges)}")
        return unsatisfied_edges 

    def get_work_days(self):
        # all except weekends - 5,6 - considering monday 0, tue 1, etc.
        return [i for i in range(len(self.days)) if i % 7 < 5]

    def total_number_of_services(self):
        cnt = 0
        for day in self.days:
            cnt += len(day.edges)
        return cnt
    
    def expected_number_of_services(self):
        res = 0
        for edge in self.demanded_edges:
            res += (self.vehicle['planning_duration'] / math.ceil(edge.freq))
        return res