

# * - make clusters
# * - cluster priority - sum of non-satisfied edges - for satisfaction see class Edge in data/read_data.py
# todo - picking among clusters - when picking cluster only take as target the non-satisfied edges
# todo - updating cluster priority - after each day, or just call heapify again - maybe do some manipulation with edge_list and next_day_streets

import sys
import heapq as hq

from util.routing_heuristic import calculate_cost, min_distance_ee

class Cluster:
    def __init__(self, edges, max_dist = 0, child_1=None, child_2=None):
        self.edges = edges
        self.max_dist = max_dist       # max distance between any 2 edges in the cluster
        self.child_1 = child_1
        self.child_2 = child_2

    def priority(self):
        # priority of cluster is equal to the sum of demand of non-satisfied edges
        # adding - (minus) in front for min-heap
        total_demand = sum(edge.demand for edge in self.edges if not edge.is_satisfied())
        return -total_demand
    
    def merge(self, other, dist):
        return Cluster(self.edges + other.edges, dist, self, other)

    def size(self):
        return len(self.edges)

    def assign_cluster(self):
        for edge in self.edges:
            edge.static_cluster = self

# for making the cut - do BFS and if a child has level < cut_level add it, else add it to queue for BFS

# todo - consider an alternative implementation where cut is made according to number of clusters if given as argument
def generate_static_clusters(edge_list):

    lvl_0_clusters = [Cluster([edge]) for edge in edge_list]
    levels = set()
    levels.add(0)

    min_distances = []
    for e1 in edge_list:
        for e2 in edge_list:
            if e1.number != e2.number:
                min_distances.append((min_distance_ee(e1, e2), e1, e2))
    hq.heapify(min_distances)

    cluster_num = len(edge_list)
    root_cluster = None
    while cluster_num > 1:
        curr_dist, e1, e2 = hq.heappop(min_distances)
        # Find the clusters containing e1 and e2
        cluster1 = e1.static_cluster
        cluster2 = e2.static_cluster

        if cluster1 == cluster2:
            continue    # skip if in same cluster

        cluster_num -= 1
        root_cluster = cluster1.merge(cluster2, curr_dist)
        levels.add(curr_dist)
        # last time root_cluster is assigned it will be the root

    # * - find cut - at biggest jump
    cut_level = -1
    max_jump = 0
    levels = list(levels)
    levels.sort()
    for i in range(0, len(levels)-1):
        jump = levels[i+1] - levels[i]
        if jump > max_jump:
            max_jump = jump
            cut_level = i+1     # everything below this will be a cluster


    # * - bfs depending on whether the child is
    # *     - below cut line (add cluster)
    # *     - or not (continue search)
    bfs_queue = [root_cluster]

    static_clusters = []
    while len(bfs_queue) > 0:
        curr_cluster = bfs_queue.pop(0)

        child_1 = curr_cluster.child_1
        child_2 = curr_cluster.child_2
        if child_1.max_dist < levels[cut_level]:
            static_clusters.append(child_1)
        else:
            bfs_queue.append(child_1)

        if child_2.max_dist < levels[cut_level]:
            static_clusters.append(child_2)
        else:
            bfs_queue.append(child_2)
    
    return static_clusters


def run(edge_list, adjacency_list, vehicle):
    # returns day_assignment list
    
    

    pass