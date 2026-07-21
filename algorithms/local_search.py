
import random
import copy
import sys
import math

sys.path.append('..')

from solution_representation.Route import Route

# * receives an sp-carp solution, on which it performs local search
# todo - every argument which is taken randomly, allow so that it can be passed as an explicit argument

# ? NOTE - ABOUT OPERATORS (OP6 AND OP7)
#   - they shouldn't be called on every edge, but on specific edges which have too many services or too little services


# task = serviced edge

# ? operator 1:
#   - take a task u on day i and move it from day i (d1) to day j (d2)
#   !- make sure to pick day d2 so that the edge is not already serviced that day - see below op1_alt comments
def op1(solution, d1, d2, e_id):
    # e_id is index of edge in day.edges


    if edge is None:
        return None
    
    if d2 in edge.service_days:
        return
    
    edge = solution.days[d1].remove_edge(edge_id = e_id)
    solution.days[d2].add_edge(edge)

    edge.service_days.remove(d1)
    edge.service_days.append(d1)
    edge.service_days.sort()

# ? alternate operator 1
#   - take a task u from day i (d1) and move it a couple days before or after to satisfy the spacing between services wrt frequency
#   - kinda finding an alternative solution to service_days, such that the difference of any 2 consecutive numbers is less than the frequency
#   - find a tight spacing and widen it so you tighten a wide spacing (greater than the frequency)
def op1_alt(solution,e_id=None):

    if e_id is None:
        edge = random.choice(solution.unsatisfied_edges())
    else:
        edge = solution.unsatisfied_edges()[e_id]
    
    if len(edge.service_days) == 0:
        # nothing to do since this op is about manipulating the service days not adding or removing
        return

    # 1. find all spacings

    # storing the number of days passed since last service, 
    # for 1st service it's days since start of planning
    # for last service it's days until end of planning
    spacings = [0] * (len(edge.service_days)+1)

    # first check at the endpoints
    # beginning - first service - 0
    spacings[0] = edge.service_days[0] - 0
    spacings[-1] = solution.vehicle['planning_duration'] - edge.service_days[-1]
    # then check between services
    for i in range(1, len(edge.service_days)):
        spacings[i] = edge.service_days[i] - edge.service_days[i-1]

    # 2. interested in the case - where there are both wide and tight spacings
    #   widen a tighter spacing to tighten a wider spacing
    #   example: 
    #       planning_duration = 28
    #       freq = 7
    #       service_days = [1, 8, 16, 23]
    #       --> spacings = [1, 7, 8, 7, 5]
    #       spacing at the end can be moved 1 day earlier and with that all of the previous services can also be shifted 1 day earlier
    #       new_service_days = [1, 8, 15, 22]
    #       now all of the spacings are less than frequency
    
    freq = math.ceil(edge.freq)
    
    tight = -1
    wide = -1
    shift = 0   # by how much the services can be shifter (forward or backward)
    for i in range(len(spacings)):
        if spacings[i] < freq:
            tight = i
            shift = freq - spacings[i]
        elif spacings[i] > freq:
            wide = i

    
    new_service_days = edge.service_days[:]
    if tight != -1 and tight < wide:
        # there is a matching pair for shifting forward
        for i in range(tight, wide-1):
            new_service_days[i+1] += shift
    elif wide != -1 and wide < tight:
        # a matching pair for shifting backward
        for i in range(tight-1, wide-1, -1):
            new_service_days[i] -= shift
    
    # print(f"Selected: {edge}")
    # print(f"Service days before: {edge.service_days}")
    # print(f"Service days after: {new_service_days}")

    for i in range(len(edge.service_days)):
        old_day = edge.service_days[i]
        new_day = new_service_days[i]
        if  old_day != new_day:
            solution.days[old_day].remove_edge(edge)
            solution.days[new_day].add_edge(edge)

    edge.service_days = new_service_days


# ? operator 2
#   - swap the service days of 2 random distinct tasks with the same frequency
def op2(solution, edge1=None, edge2=None):

    demanded_edges = solution.demanded_edges
    
    if edge1 is None:
        edge1 = random.choice(demanded_edges)

    if edge2 is None:
        same_freq = [e for e in demanded_edges if e.freq == edge1.freq and e != edge1]

        edge2 = random.choice(same_freq)

    if edge1.freq != edge2.freq:
        # don't do anything if arguments are given for edges with different frequency
        return

    for d in edge1.service_days:
        solution.days[d].remove_edge(edge1)
        solution.days[d].add_edge(edge2, recalculate = False)

    for d in edge2.service_days:
        solution.days[d].remove_edge(edge2)
        solution.days[d].add_edge(edge1, recalculate = False)

    # recalculate routes after swapping the service days of both edges
    affected_days = set(edge1.service_days + edge2.service_days)
    for d in affected_days:
        solution.days[d].recalculate_routes()

    temp = edge1.service_days.copy()
    edge1.service_days = edge2.service_days
    edge2.service_days = temp
    
    return edge1, edge2

# ? operator 3
#   - two-opt
#   - from 1 route containing a sequence (a,b) and another route containing a sequence (c,d)
#   - disconnect a-b and c-d and connect it with the other like a-d and c-b
#   - the routes are from the same day (d1)
#   - allow a route to be taken whole - like not cut it all (ie cut before beginning of route or cut after end of route)
def op3(solution, d1=None):
    # possible combinatins
    # ac bd, ad bc - everything else is same cb is same as bc (same cost otherwise same route)
    # basically cut 2 routes in half and connect a half with a half from the other route

    if d1 is None:
        d1 = random.choice(solution.get_work_days())
    
    day = solution.days[d1]

    # if the day has only one route
    if day.route_count <= 1:
        return
    
    # take 2 distinct routes
    r1, r2 = random.sample(day.routes, 2)

    # remove the routes from the day
    day.remove_route(r1)
    day.remove_route(r2)

    cut1 = random.randint(0, len(r1.targets) - 1)
    cut2 = random.randint(0, len(r2.targets) - 1)

    r1_h1 = Route(r1.targets[:cut1])
    r1_h2 = Route(r1.targets[cut1:])

    r2_h1 = Route(r2.targets[:cut2])
    r2_h2 = Route(r2.targets[cut2:])

    # print(r1_h1)
    # print(r1_h2)
    # print(r2_h1)
    # print(r2_h2)
    
    a_r1 = r1_h1.merge(r2_h2)
    a_r2 = r1_h2.merge(r2_h1)

    b_r1 = r1_h1.merge(r2_h1)
    b_r2 = r1_h2.merge(r2_h2)

    cost_a = a_r1.length + a_r2.length
    cost_b = b_r1.length + b_r2.length

    # add the new routes depending on which combination is cheaper
    if cost_a < cost_b:
        res_r1 = a_r1
        res_r2 = a_r2
    else:
        res_r1 = b_r1
        res_r2 = b_r2

    day.add_route(res_r1)
    day.add_route(res_r2)
    return r1, r2, res_r1, res_r2

# ? operator 4
#   - take a task u and move it to a different route within the same day
#   - consider all spots in 1 route where it can be put in - think I can use binary search here
#   - or an alternative to consider only adding it at the end/beginning of a route, but try it for all routes
def op4(solution, d1=None, edge1=None, edge2=None):

    if d1 is None:
        d1 = random.choice(solution.get_work_days())

    day = solution.days[d1]

    # print(f"Day {d1} has {len(day.routes)} routes.")

    # random for testing
    if edge1 is None:
        route1, route2 = random.sample(day.routes, 2)
        edge1 = random.choice(route1.targets)
        edge2 = random.choice(route2.targets)

        # route1.set_target_routes()
        # route2.set_target_routes()

    if edge1 not in day.edges or edge2 not in day.edges:
        return

    route_2 = day.get_edge_route(edge2)
    
    day.remove_edge(edge1)
    route_2.insert_edge(edge1, edge_in_route = edge2)



# ? operator 5
#   - similar to op4, but take 2 successive tasks performed one after another and move them together as a sequence
#   - again consider all possible places
def op5(solution, d1=None, edge_a1=None, edge_a2=None, edge_b=None):
    # take successive edges edge_a1, edge_a2 from route A and insert them before edge_b of route B
    # with route A != route B

    day = solution.days[d1]
    if edge_a1 not in day.edges or edge_a2 not in day.edges or edge_b not in day.edges:
        # only change routes within a day
        return

    a1_route = day.get_edge_route(edge_a1)
    a2_route = day.get_edge_route(edge_a2)
    b_route = day.get_edge_route(edge_b)

    if a1_route != a2_route:
        # not checking for successiveness
        # maybe can just give 1 edge as an argument and take the next one implicitly 
        # only if the given edge is not the last edge
        return
    
    if a1_route == b_route:
        # todo - will decide on this behaviour later
        return
    
    day.remove_edge(edge_a1)
    day.remove_edge(edge_a2)

    # b
    b_route.insert_edge(edge_a2, edge_in_route = edge_b)
    # a2 b
    b_route.insert_edge(edge_a1, edge_in_route = edge_a2)
    # a1 a2 b


# ? operator 6
#   - remove a single service of an edge on some day
def op6(solution, d1, edge):

    solution.days[d1].remove_edge(edge)

    try:
        edge.service_days.remove(d1)
    except:
        # in case it's called with a day on which the edge is not serviced
        pass

# ? operator 7
#   - add a single service of an edge on a day
#   - only if the edge is not already serviced on that day
def op7(solution, d1, edge):

    if d1 not in solution.get_work_days():
        # don't add edges for service to a non-work day (weekend)
        return
    elif d1 in edge.service_days:
        # if the edge is already serviced in that day
        return
    
    solution.days[d1].add_edge(edge)
    # with the spacing penalty - the proper day will have more priority


def run(solution):

    
    
    no_improvement_count = 0
    patience = 10       # how many iterations to go without improvement

    current_best_solution = solution
    neighbour_opX_solution = copy.deepcopy(current_best_solution)

    best_score = current_best_solution.evaluate()
    neighbour_score = best_score        # just a placeholder number
    while no_improvement_count < patience:
        # todo - change above operators so they take proper arguments
        pass
        break

