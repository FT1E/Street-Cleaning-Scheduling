
import re
import os, sys
import pandas as pd
from enum import Enum

graph_data_filepath = './SP-CARP graphs/SP-CARP_F1_g_graph.dat' 
vehicle_data_filepath = './SP-CARP vehicles/SP-CARP_1-2.veh'


graph_data_directory = os.path.join('D:\\','Seminar', 'data', 'SP-CARP graphs')
vehicle_data_directory = os.path.join('D:\\','Seminar', 'data', 'SP-CARP vehicles')

# for file in os.listdir(graph_data_directory):
#     with open(os.path.join(graph_data_directory, file), 'r') as graph_file:
#         graph_data = graph_file.read()
#         lines = graph_data.splitlines()
        
        # num_fractions = int(re.sub(r'.*:\s*', '', lines[4]))


PriorityType = Enum('PriorityType', {'Frequency' : 0, 'Deadline' : 1, 'Distance' : 2})

class Edge:
    def __init__(self, number, start_node, end_node, demand, distance, freq, priority_type = PriorityType.Deadline, last_cleaning_day=0, curr_day=0):
        self.number = number
        self.start_node = start_node
        self.end_node = end_node
        self.demand = demand
        self.distance = distance
        self.freq = freq
        self.curr_day = curr_day
        self.last_cleaning_day = last_cleaning_day      # irrelevant for streets which are cleaned only once in time duration
        self.priority_type = priority_type
        self.route = -1

    def __lt__(self, other):
        return self.priority() - other.priority()
    
    def priority(self):
        match self.priority_type:
            case PriorityType.Deadline:
                return self.freq - + self.last_cleaning_day
            case PriorityType.Frequency:
                return self.freq
            case PriorityType.Distance:
                return self.distance
            case _:
                print("Not defined priority type for class Edge!")
                return None
    
    def set_curr_day(self, day):
        self.curr_day = day

    def set_cleaning_day(self, day):
        self.last_cleaning_day = day

    def __repr__(self):
        return f"Edge: {self.start_node} --> {self.end_node}"

    # below to avoid assigning a duplicate edge in the same day
    def __eq__(self, value):
        if not isinstance(value, Edge):
            return False
        return (self.start_node == value.start_node and self.end_node == value.end_node) or (self.start_node == value.end_node and self.end_node == value.start_node)

# get data for graph i
# list of all edges for graph i
def get_graph_edge_list(i):
    try:
        file = os.listdir(graph_data_directory)[i]
    except IndexError:
        print('Index out of range for file!')
        return None
    except:
        print("Some other error while reading file")
        return None

    with open(os.path.join(graph_data_directory, file), 'r') as f:
        graph_data = f.read()

        lines = graph_data.splitlines()
    
        # * number of edges
        num_edges = int(re.sub(r'.*:\s*', '', lines[2]))

        # * in the first few files it's 0, but not in all of them
        depot_node = int(re.sub(r'.*:\s*', '', lines[3]))

        # * note fraction == trash type
        fraction_line = lines[5].split('\t')
        fraction_type = fraction_line[1]
        num_of_intervals = int(fraction_line[2])
        intervals = [float(x) for x in fraction_line[3:]]

        edge_header = lines[7].split('\t')
        edge_table = [x.split('\t') for x in lines[9:9+num_edges]]
        edge_data = pd.DataFrame(edge_table, columns = edge_header)

        
        edge_data = edge_data.drop([f"Bins_{i}" for i in range(num_of_intervals)], axis=1)


        # * converting data to numeric
        edge_data = edge_data.apply(pd.to_numeric)

        return [Edge(e.EdgeNumber, e.StartNodeNumber, e.EndNodeNumber, -1, e.Cost, -1) for e in edge_data.itertuples(False)]


# list of edges with non-zero demand
def get_graph_demanded_edges(i):
    
    try:
        file = os.listdir(graph_data_directory)[i]
        # print(f"Graph file read: {file}")
    except IndexError:
        print('Index out of range for file!')
        return None
    except:
        print("Some other error while reading file")
        return None

    with open(os.path.join(graph_data_directory, file), 'r') as f:
        graph_data = f.read()

        lines = graph_data.splitlines()
    
        # * number of edges
        num_edges = int(re.sub(r'.*:\s*', '', lines[2]))

        # * in the first few files it's 0, but not in all of them
        depot_node = int(re.sub(r'.*:\s*', '', lines[3]))

        # * note fraction == trash type
        fraction_line = lines[5].split('\t')
        fraction_type = fraction_line[1]
        num_of_intervals = int(fraction_line[2])
        intervals = [float(x) for x in fraction_line[3:]]

        edge_header = lines[7].split('\t')
        edge_table = [x.split('\t') for x in lines[9:9+num_edges]]
        edge_data = pd.DataFrame(edge_table, columns = edge_header)

        # * drop number of bins, only keep demand for now
        # todo - in future consider number of bins as well
        edge_data = edge_data.drop([f"Bins_{i}" for i in range(num_of_intervals)], axis=1)

        # * converting data to numeric
        edge_data = edge_data.apply(pd.to_numeric)

        # * - assign frequency to each edge
        edge_frequencies = [None] * num_edges

        for tuple in edge_data.itertuples(False):
            edge_frequencies[tuple.EdgeNumber] = [intervals[i] for i in range(num_of_intervals) if getattr(tuple, f'Demand_{i}') != 0]

        non_zero_edges = pd.DataFrame([ [i , edge_frequencies[i], min(edge_frequencies[i]), max(edge_frequencies[i])] for i in range(len(edge_frequencies)) if len(edge_frequencies[i]) > 0], columns = ['EdgeNumber', 'Frequencies', 'MinFrequency', 'MaxFrequency'])

        

        non_zero_edges = pd.merge(edge_data, non_zero_edges, on='EdgeNumber')

        # todo - chose min frequency and the demand associated with that frequency
        return [Edge(e.EdgeNumber, e.StartNodeNumber, e.EndNodeNumber, getattr(e, edge_header[5 + 2*intervals.index(e.MinFrequency)]), e.Cost, e.MinFrequency) for e in non_zero_edges.itertuples(False)]
    
    return None

def get_graph_metadata(i):
    try:
        file = os.listdir(graph_data_directory)[i]
        # print(f"Graph file read: {file}")
    except IndexError:
        print('Index out of range for file!')
        return None
    except:
        print("Some other error while reading file")
        return None

    with open(os.path.join(graph_data_directory, file), 'r') as f:
        graph_data = f.read()

        lines = graph_data.splitlines()
    
        # * number of nodes/vertices
        num_nodes = int(re.sub(r'.*:\s*', '', lines[1]))
        
        # * number of edges
        num_edges = int(re.sub(r'.*:\s*', '', lines[2]))

        # * in the first few files it's 0, but not in all of them
        depot_node = int(re.sub(r'.*:\s*', '', lines[3]))

        return {'num_nodes' : num_nodes, 'num_edges' : num_edges, 'depot_node' : depot_node}

# get adjacency list for graph i
def get_graph_al(i, priority_type = PriorityType.Deadline):
    raw_graph_data = get_graph_edge_list(i)
    if raw_graph_data is None:
        return      # log messages in get_graph_data
    
    graph_metadata = get_graph_metadata(i)
    # not checking for None value on this - since if above works so should this
    # print(graph_metadata)

    adjacency_list = [[] for _ in range(graph_metadata['num_nodes'])]
    for edge in raw_graph_data:
        adjacency_list[edge.start_node].append(edge)
        edge.priority_type = priority_type

        # same edge just swap start_node and end_node
        reverse_edge = Edge(edge.number, edge.end_node, edge.start_node, edge.demand, edge.distance, edge.freq, priority_type)
        adjacency_list[edge.end_node].append(reverse_edge)

    # for i in range(len(adjacency_list)):
    #     print(f"Node {i} adjacency list:")
    #     for edge in adjacency_list[i]:
    #         print(edge, end='\t')
    #     print('\n')

    # print(f"Number of adjacency lists: {len(adjacency_list)}")
    # print('\n\n')

    
    return adjacency_list

# get data
def get_vehicle_data(i):

    try:
        file = os.listdir(vehicle_data_directory)[i]
    except IndexError:
        print('Index out of range for file!')
        return None
    except:
        print("Some other error while reading file")
        return None

    with open(os.path.join(vehicle_data_directory, file), 'r') as f:
        vehicle_data = f.read()
        lines = vehicle_data.splitlines()

        planning_duration = int(lines[0].split('\t')[1]) 
        

        days_no_service = [int(x) for x in lines[4].split('\t')[3:]]

        capacity = int(lines[10].split('\t\t\t')[1])
        
        speed = int(lines[14].split('\t\t\t')[1])
        time_limit = int(lines[17].split('\t\t\t')[1])

        distance_limit = speed * time_limit

        return {'planning_duration' : planning_duration, 'days_no_service': days_no_service, 'capacity' : capacity, 'distance_limit' : distance_limit}


