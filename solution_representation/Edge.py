
from enum import Enum
import math

# used to represent an Edge which belongs to a route in a solution
# also used in the greedy algorithms to represent an edge list from which an edge is picked in a greedy way

# below copied from Solution.py
EXPECTED_SERVICES_PENALTY = 1_000_000       # multiply by number of edges who have too few or too many services
EXPECTED_SPACING_PENALTY = 500_000        # multiplied by number of spacings which are too tight or too wide



PriorityType = Enum('PriorityType', {'Frequency' : 0, 'Deadline' : 1, 'Distance' : 2})

class Edge:
    def __init__(self, number, start_node, end_node, demand, distance, freq, priority_type = PriorityType.Deadline, last_cleaning_day=-1, curr_day=0):
        
        # id - note some edges may have same id but different endpoints
        # so in equality check it's checked that edges have same id and same endpoints
        # to differentiate duplicate edges - for edges with more than 1 frequency type
        self.number = number
        
        # end-nodes
        self.start_node = start_node
        self.end_node = end_node
        
        # demand, distance, frequency
        self.demand = demand
        self.distance = distance
        self.freq = freq

        # for static clustering algorithm
        self.static_cluster = None

        # run-time info
        self.curr_day = curr_day
        self.last_cleaning_day = last_cleaning_day      # irrelevant for streets which are cleaned only once in time duration
        self.priority_type = priority_type
        self.route = None

        self.service_days = []


    def __lt__(self, other):
        return self.priority() < other.priority()
    
    def priority(self):
        match self.priority_type:
            case PriorityType.Deadline:
                return self.freq + self.last_cleaning_day
            case PriorityType.Frequency:
                return self.freq
            case PriorityType.Distance:
                return self.distance
            case _:
                print("Undefined priority type for class Edge!")
                return None
    
    def set_curr_day(self, day):
        self.curr_day = day

    def set_cleaning_day(self, day):
        self.last_cleaning_day = day
        self.service_days.append(day)

    def __repr__(self):
        return f"Edge: {self.start_node} <--> {self.end_node} \t Freq: {self.freq} \t Demand: {self.demand}"

    # below to avoid assigning a duplicate edge in the same day
    def __eq__(self, value):
        if not isinstance(value, Edge):
            return False
        return self.number == value.number and ((self.start_node == value.start_node and self.end_node == value.end_node) or (self.start_node == value.end_node and self.end_node == value.start_node))

    # used for static clustering - satisfied if since last cleaning day, less than half the frequency days have passed
    def is_satisfied(self, curr_day = None):
        if self.last_cleaning_day < 0:
            return False
        
        if curr_day is not None:
            self.curr_day = curr_day
        return self.last_cleaning_day + self.freq // 2 < self.curr_day


    def is_under_satisfied(self, vehicle):
        service_count = len(self.service_days)
        expected_service_count = math.floor(vehicle['planning_duration'] / math.ceil(self.freq))
        if service_count < expected_service_count:
            return True
        return False


    def is_over_satisfied(self, vehicle):
        service_count = len(self.service_days)
        expected_service_count = math.ceil(vehicle['planning_duration'] / math.ceil(self.freq))
        if service_count > expected_service_count:
            return True
        return False


    def spacing_cost(self, vehicle):
        cost = 0
        
        if len(self.service_days) == 0:
            cost += math.floor(vehicle['planning_duration'] / math.ceil(self.freq)) * EXPECTED_SPACING_PENALTY
            return cost

        expected_spacing = math.ceil(self.freq)

        spacing = self.service_days[0]

        if spacing > expected_spacing + self.freq // 7 or spacing < expected_spacing:
            cost += EXPECTED_SPACING_PENALTY

        spacing = vehicle['planning_duration'] - self.service_days[-1]

        if spacing > expected_spacing + self.freq // 7 or spacing < expected_spacing:
                    cost += EXPECTED_SPACING_PENALTY

        for i in range(len(self.service_days) - 1):
            spacing = self.service_days[i+1] - self.service_days[i]
            if spacing > expected_spacing + self.freq // 7 or spacing < expected_spacing:
                cost += EXPECTED_SPACING_PENALTY

        return cost

    def add_service_day(self, day):
        for i in range(len(self.service_days)):
            if self.service_days[i] > day:
                self.service_days.insert(i, day)
                return
    
        # in case it's the last service
        self.service_days.append(day)