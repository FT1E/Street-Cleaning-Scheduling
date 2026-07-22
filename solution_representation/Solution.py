
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


VEHICLE_WEIGHT = 100_000                    # multiply by number of vehicles used for whole sp-carp, ie the minimum num of vehicles needed, ie maximum number of vehicles among days
VEHICLE_OVERLOAD_PENALTY = 1_000_000        # when a route has total demand or length greater than what vehicle can handle - multiply by number of routes which violate 
EXPECTED_SERVICES_PENALTY = 1_000_000       # multiply by number of edges who have too few or too many services
EXPECTED_SPACING_PENALTY = 500_000        # multiplied by number of spacings which are too tight or too wide
# last one is lower since i'm expecting there to be a lot of those violations - at least at the beginning
# todo - may set it higher

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
        
        # for op2
        self.frequency_buckets = dict()
        self.init_freq_buckets()

    
    def __repr__(self):
        self.print()
        return ""

    def print(self):
        for day in self.days:
            day.print()

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
        overload_route_count = 0        # number of routes which can't be handled by a single vehicle, go over the limits
        for day in self.days:
            routing_cost += day.total_distance
            vehicle_count = max(vehicle_count, day.route_count)

            for route in day.routes:
                if route.length > self.vehicle['distance_limit'] or route.demand > self.vehicle['capacity']:
                    overload_route_count += 1

        irregular_spacing_count = 0
        for edge in self.demanded_edges:
            if len(edge.service_days) == 0:
                # for edges which weren't serviced at all
                irregular_spacing_count += self.vehicle['planning_duration'] // math.ceil(edge.freq)

            expected_spacing = math.floor(edge.freq)

            # spacing between beginning of planning and 1st service - edge.service_days[0] - first_day (0)
            spacing = edge.service_days[0]
            if self.irregular_spacing_check(spacing, expected_spacing):
                irregular_spacing_count += 1
            # spacing between end of planning and last service
            spacing = self.vehicle['planning_duration'] - edge.service_days[-1]
            if self.irregular_spacing_check(spacing, expected_spacing):
                irregular_spacing_count += 1
            
            for i in range(len(edge.service_days) - 1):
                spacing = edge.service_days[i+1] - edge.service_days[i]
                if self.irregular_spacing_check(spacing, expected_spacing):
                    irregular_spacing_count += 1

        cost = routing_cost + VEHICLE_WEIGHT * vehicle_count + VEHICLE_OVERLOAD_PENALTY * overload_route_count + EXPECTED_SPACING_PENALTY * irregular_spacing_count
        return cost

    # if true - spacing is too wide or too tight
    def irregular_spacing_check(self, spacing, expected_spacing):
        return spacing > expected_spacing + 1 or spacing < expected_spacing - expected_spacing // 7
        

    # for checking if all edges had their frequency satisfied
    def unsatisfied_edges(self):
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

    def over_satisfied_edges(self):
        over_satisfied_edges = []
        for edge in self.demanded_edges:
            service_count = len(edge.service_days)
            expected_service_count = self.vehicle['planning_duration'] / math.ceil(edge.freq)
            if service_count > self.expected_number_of_services:
                self.over_satisfied_edges.append(edge)

        return over_satisfied_edges


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
    
    def checking_references(self):
        cnt = 0
        for day_1 in self.days:
            for edge_1 in day_1.edges:
                for day_2 in self.days:
                    if day_1 == day_2:
                        continue
                    for edge_2 in day_2.edges:
                        if edge_1 is edge_2:
                            cnt += 1

        print(f"{cnt} edges have same instances in different days")

    # for op2 - instead of skipping to just directly get the needed edges
    def init_freq_buckets(self):
        for edge in self.demanded_edges:
            if edge.freq not in self.frequency_buckets:
                self.frequency_buckets[edge.freq] = [edge]
            else:
                self.frequency_buckets[edge.freq].append(edge)