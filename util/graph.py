
# todo - convert graph data into adjacency lists with elements of this type

class Edge:

    def __init__(self, start_node, end_node, distance, demand):
        self.start_node = start_node
        self.end_node = end_node
        self.distance = distance
        self.demand = demand
        self.route = -1     # used for calculating routing cost

    def __lt__(self, other):
        return self.distance < other.weight