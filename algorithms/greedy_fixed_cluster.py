

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
    
    def num_non_satisfied_edges(self):
        res = 0
        for edge in self.edges:
            if not edge.is_satisfied(self.curr_day):
                res += 1
        return res

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

    def __lt__(self, other):
        return self.priority() < other.priority()

# for making the cut - do BFS and if a child has level < cut_level add it, else add it to queue for BFS

# todo - consider an alternative implementation where cut is made according to number of clusters if given as argument
def generate_static_clusters(edge_list, adjacency_list, vehicle):

    calculate_distances(adjacency_list)

    lvl_0_clusters = [Cluster([edge]) for edge in edge_list]
    for cluster in lvl_0_clusters:
        cluster.assign_cluster()

    min_distances = []
    for e1 in edge_list:
        for e2 in edge_list:
            if e1.number != e2.number:
                min_distances.append((min_distance_ee(e1, e2), e1, e2))
    hq.heapify(min_distances)

    cluster_num = len(edge_list)

    static_clusters = []
    merged_cluster = None
    while cluster_num > 1:
        curr_dist, e1, e2 = hq.heappop(min_distances)
        # Find the clusters containing e1 and e2
        cluster1 = e1.static_cluster
        cluster2 = e2.static_cluster

        if cluster1 == cluster2:
            continue    # skip if in same cluster

        if cluster1.demand() + cluster2.demand() > vehicle['capacity']:
            # add them to return res
            static_clusters.append(cluster1)
            static_clusters.append(cluster2)
            
            cluster_num -= 2
            continue

        cluster_num -= 1
        merged_cluster = cluster1.merge(cluster2, curr_dist)
        merged_cluster.assign_cluster()
        # last time root_cluster is assigned it will be the root

    print(f'[DEBUG]: cluster_num == {cluster_num}')
   
    return static_clusters

def generate_cw_clusters(edge_list, adjacency_list, vehicle):
    # generate static clusters by giving all of the edges as targets to Clarke-Wright 
    # and turning each route into a static cluster
    routing_info = calculate_cost(adjacency_list, edge_list, vehicle)

    cw_clusters = []
    for route in routing_info['routes']:
        cw_clusters.append(Cluster(route.targets))
        cw_clusters[-1].assign_cluster()

    return cw_clusters

def run(edge_list, adjacency_list, vehicle):
    # returns day_assignment list
    
    day_assignment = [[] for _ in range(vehicle['planning_duration'])]
    capacity_used = [0] * vehicle['planning_duration']

    clusters = generate_cw_clusters(edge_list, adjacency_list, vehicle)
    next_day_clusters = []

    hq.heapify(clusters)

    for day in range(vehicle['planning_duration']):
        if day+1 in vehicle['days_no_service']:
            continue
        
        # update curr_day in every cluster
        for cluster in clusters:
            cluster.curr_day = day


        # todo - optimize below stuff later, so it doesn't use too much memory

        # re-sort it
        clusters = list(clusters)
        hq.heapify(clusters)
        clusters = list(hq.merge(clusters, next_day_clusters))
        next_day_clusters = []


        while capacity_used[day] < vehicle['capacity'] and len(clusters) > 0:
            cluster = hq.heappop(clusters)

            if cluster.num_non_satisfied_edges() == 0:
                # meaning that all clusters further will also have no demanding edges
                print(f'Breaking for day {day+1}')
                hq.heappush(next_day_clusters, cluster) # push it back so it gets assigned the next day
                break   # go to next day

            if capacity_used[day] + cluster.demand() < vehicle['capacity']:
                # if cluster has higher demand than the vehicle can handle for the day then skip it for today
                hq.heappush(next_day_clusters, cluster)
                continue

            # todo - check for routing cost - not above limit, easy to check for the cw_clusters

            # ? note that this assigns only non-satisfied edges
            capacity_used[day] += cluster.demand()
            new_edges = cluster.assign_egdges_to_cleaning_day(day)
            day_assignment[day].extend(new_edges)

            hq.heappush(next_day_clusters, cluster)     # push cluster back

    return day_assignment, capacity_used