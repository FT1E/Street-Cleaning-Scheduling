
import re
import os, sys
import pandas as pd

graph_data_filepath = './data/SP-CARP graphs/SP-CARP_F1_g_graph.dat' 
vehicle_data_filepath = './data/SP-CARP vehicles/SP-CARP_1-2.veh'


with open(graph_data_filepath, 'r') as graph_file:
    graph_data = graph_file.read()

    lines = graph_data.splitlines()
    
    # * number of edges
    num_edges = int(re.sub(r'.*:\s*', '', lines[2]))
    # print(num_edges)
    

    # * in the first few files it's 0, but not in all of them
    depot_node = int(re.sub(r'.*:\s*', '', lines[3]))
    # print(depot_node)

    
    # * note fraction == trash type
    fraction_line = lines[5].split('\t')
    fraction_type = fraction_line[1]
    num_of_intervals = int(fraction_line[2])
    intervals = [float(x) for x in fraction_line[3:]]
    
    # print(fraction_line)
    # print(fraction_type)
    # print(intervals)

    edge_header = lines[7].split('\t')
    
    # num_edges = 5       # // todo - comment this line out later for reading whole data

    edge_table = [x.split('\t') for x in lines[9:9+num_edges]]
    edge_data = pd.DataFrame(edge_table, columns = edge_header)
    
    # print(edge_data)

    # interval_data = edge_data[[x for x in edge_header[5:]]]
    
    # bin_number = lambda i : f"bins_{i}"
    # bin_demand = lambda i : f"demand_{i}"
    # interval_data.columns = [f(x) for x in intervals for f in (bin_number, bin_demand)]
    
# * drop number of bins, only keep demand for now
# todo - in future consider number of bins as well
edge_data = edge_data.drop([f"Bins_{i}" for i in range(num_of_intervals)], axis=1)


# * converting data to numeric
edge_data = edge_data.apply(pd.to_numeric)

# * - assign frequency to each edge
edge_frequencies = [None] * num_edges

for tuple in edge_data.itertuples(False):
    # print(tuple)
    edge_frequencies[tuple.EdgeNumber] = [intervals[i] for i in range(num_of_intervals) if getattr(tuple, f'Demand_{i}') != 0]
    

# print('\n'.join([str(x) for x in edge_frequencies]))


non_zero_edges = pd.DataFrame([ [i , edge_frequencies[i], min(edge_frequencies[i]), max(edge_frequencies[i])] for i in range(len(edge_frequencies)) if len(edge_frequencies[i]) > 0], columns = ['EdgeNumber', 'Frequencies', 'MinFrequency', 'MaxFrequency'])

non_zero_edges = pd.merge(edge_data[edge_header[:5]], non_zero_edges, on='EdgeNumber')

print('\nEdges with non-zero frequencies\n')
print(non_zero_edges)




graph_data_directory = './data/SP-CARP graphs/'

# for file in os.listdir(graph_data_directory):
#     with open(os.path.join(graph_data_directory, file), 'r') as graph_file:
#         graph_data = graph_file.read()
#         lines = graph_data.splitlines()
        
        # num_fractions = int(re.sub(r'.*:\s*', '', lines[4]))


