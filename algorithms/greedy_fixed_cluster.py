

# * - make clusters
# * - cluster priority - sum of non-satisfied edges - for satisfaction see class Edge in data/read_data.py
#   * - edge is satisfied if since last cleaning day, less than half the frequency days have passed
# * - picking among clusters - when picking cluster only take as target the non-satisfied edges
# todo - some debugging - if some cluster size exceeds than what the vehicle can handle
#   todo - implement in generating the clusters if cluster cost or demand exceeds than what a single vehicle can handle then keep exploring

import sys
import heapq as hq

from util.routing_heuristic import calculate_cost, min_distance_ee, calculate_distances

class Cluster:
    def __init__(self, edges, max_dist = 0, child_1=None, child_2=None):
        self.edges = edges
        self.max_dist = max_dist       # max distance between any 2 edges in the cluster
        self.child_1 = child_1
        self.child_2 = child_2
        self.curr_day = -1

    def priority(self):
        # priority of cluster is equal to the sum of priority of non-satisfied edges
        total = sum(edge.priority() for edge in self.edges if not edge.is_satisfied(self.curr_day))
        return total
    
    def demand(self):
        return sum(edge.demand for edge in self.edges if not edge.is_satisfied(self.curr_day))
    
    def merge(self, other, dist):
        return Cluster(self.edges + other.edges, dist, self, other)

    def size(self):
        return len(self.edges)
    
    def num_satisfied_edges(self):
        return sum(1 for edge in self.edges if edge.is_satisfied(self.curr_day))

    def assign_cluster(self):
        for edge in self.edges:
            edge.static_cluster = self

    def assign_egdges_to_cleaning_day(self, cleaning_day):
        # returns the edges which were assigned
        res = []
        for edge in self.edges:
            if not edge.is_satisfied(self.curr_day):
                edge.set_cleaning_day(cleaning_day)
                res.append(edge)

        return res

# for making the cut - do BFS and if a child has level < cut_level add it, else add it to queue for BFS

# todo - consider an alternative implementation where cut is made according to number of clusters if given as argument
def generate_static_clusters(edge_list, adjacency_list):

    calculate_distances(adjacency_list)

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

    for cluster in static_clusters:
        cluster.assign_cluster()
        cluster.curr_day = 0

    return static_clusters


def run(edge_list, adjacency_list, vehicle):
    # returns day_assignment list
    
    day_assignment = [[] for _ in range(vehicle['planning_duration'])]
    capacity_used = [0] * vehicle['planning_duration']

    clusters = generate_static_clusters(edge_list, adjacency_list)
    next_day_clusters = []

    hq.heapify(clusters)

    for day in range(vehicle['planning_duration']):
        if day in vehicle['days_no_service']:
            continue
        
        clusters = list(hq.merge(clusters, next_day_clusters))
        next_day_clusters = []

        # update curr_day in every cluster
        for cluster in clusters:
            cluster.curr_day = day

        while capacity_used[day] < vehicle['capacity'] and len(clusters) > 0:
            cluster = hq.heappop(clusters)

            if cluster.num_satisfied_edges() == 0:
                # meaning that all clusters further will also have no demanding edges
                break   # go to next day

            if capacity_used[day] + cluster.priority() < vehicle['capacity']:
                # if cluster has higher demand than the vehicle can handle for the day then skip it for today
                hq.heappush(next_day_clusters, cluster)
                continue

            # ? note that this assigns only non-satisfied edges
            day_assignment[day] += cluster.assign_egdges_to_cleaning_day(day)
            capacity_used[day] += cluster.priority()

    return day_assignment