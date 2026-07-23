
import random
import copy
import sys
import math

import time

sys.path.append('..')

from solution_representation.Route import Route

# * receives an sp-carp solution, on which it performs local search

# ? NOTE - ABOUT OPERATORS (OP6 AND OP7)
#   - they shouldn't be called on every edge, but on specific edges which have too many services or too little services


# weights copied for estimating a delta on the cost instead of whole re-evaluation
VEHICLE_WEIGHT = 100_000                    # multiply by number of vehicles used for whole sp-carp, ie the minimum num of vehicles needed, ie maximum number of vehicles among days
VEHICLE_OVERLOAD_PENALTY = 1_000_000        # when a route has total demand or length greater than what vehicle can handle - multiply by number of routes which violate 
EXPECTED_SERVICES_PENALTY = 1_000_000       # multiply by number of edges who have too few or too many services
EXPECTED_SPACING_PENALTY = 500_000        # multiplied by number of spacings which are too tight or too wide


# todo - shaking procedure


# task = serviced edge

# ? operator 1:
#   - take a task u on day i and move it from day i (d1) to day j (d2)
#   !- make sure to pick day d2 so that the edge is not already serviced that day - see below op1_alt comments
def op1(solution, d1, d2, edge= None, edge_id = None):
    # e_id is index of edge in day.edges

    if edge is None and edge_id is not None:
        edge = solution.days[d1].edges[edge_id]
    elif edge is None:
        return None

    if d2 in edge.service_days:
        # if this is the case, then it's the same as just removing the service (op6)
        return None
    

    solution.days[d1].remove_edge(edge)
    solution.days[d2].add_edge(edge)

    edge.service_days.remove(d1)
    edge.service_days.append(d2)
    edge.service_days.sort()

    return True

def undo_op1(solution, day_1, day_2, edge=None, edge_id=None):

    if edge is None and edge_id is not None:
        edge = solution.days[day_1].edges[edge_id]
    elif edge is None:
        return None
    
    solution.days[day_2].remove_edge(edge, recalculate=True)
    solution.days[day_1].add_edge(edge)
    edge.service_days.remove(day_2)
    edge.service_days.append(day_1)
    edge.service_days.sort()

# ? alternate operator 1
#   - take a task u from day i (d1) and move it a couple days before or after to satisfy the spacing between services wrt frequency
#   - kinda finding an alternative solution to service_days, such that the difference of any 2 consecutive numbers is less than the frequency
#   - find a tight spacing and widen it so you tighten a wide spacing (greater than the frequency)
def op1_alt(solution,edge=None, edge_id=None):

    if edge is None and edge_id is not None:
        edge = solution.unsatisfied_edges()[edge_id]
    elif edge is not None and edge not in solution.unsatisfied_edges():
        # if the edge already has satisfied spacing 
        return None
    else:
        # either no arguments given or the edge already has satisfied frequency
        return None
    
    if len(edge.service_days) == 0:
        # nothing to do since this op is about manipulating the service days not adding or removing
        return None

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
    return True


# ? operator 2
#   - swap the service days of 2 random distinct tasks with the same frequency
def op2(solution, edge1=None, edge2=None):

    
    if edge1 is None or edge2 is None:
        # can't do anything if not enough arguments are given
        return None
    

    if edge1.freq != edge2.freq:
        # don't do anything if arguments are given for edges with different frequency
        return None

    for d in edge1.service_days:
        solution.days[d].remove_edge(edge1)

    for d in edge2.service_days:
        solution.days[d].remove_edge(edge2)

    for d in edge1.service_days:
        solution.days[d].add_edge(edge2, recalculate = False)
        
    for d in edge2.service_days:
        solution.days[d].add_edge(edge1, recalculate = False)


    # recalculate routes after swapping the service days of both edges
    affected_days = set(edge1.service_days + edge2.service_days)
    for d in affected_days:
        solution.days[d].recalculate_routes()

    temp = edge1.service_days.copy()
    edge1.service_days = edge2.service_days
    edge2.service_days = temp
    
    return True


def undo_op2(solution, edge1, edge2):
    op2(edge1, edge2)


# ? operator 3
#   - two-opt
#   - from 1 route containing a sequence (a,b) and another route containing a sequence (c,d)
#   - disconnect a-b and c-d and connect it with the other like a-d and c-b
#   - the routes are from the same day (d1)
#   - allow a route to be taken whole - like not cut it all (ie cut before beginning of route or cut after end of route)
def op3(solution, route_1, route_2, r1_cutpoint, r2_cutpoint):
    # possible combinatins
    # ac bd, ad bc - everything else is same cb is same as bc (same cost otherwise same route)
    # basically cut 2 routes in half and connect a half with a half from the other route

    if route_1.day.number != route_2.day.number:
        # if in different days don't do anything
        # comparing the number to save on time
        return None
    
    day = route_1.day

    # remove the routes from the day
    day.remove_route(route_1)
    day.remove_route(route_2)

    delta_cost -= (route_1.evaluate(solution.vehicle) + route_2.evaluate(solution.vehicle))
    

    route_1_half_1 = Route(route_1.targets[:r1_cutpoint])
    route_1_half_2 = Route(route_1.targets[r1_cutpoint:])

    route_2_half_1 = Route(route_2.targets[:r2_cutpoint])
    route_2_half_2 = Route(route_2.targets[r2_cutpoint:])

    # try both combinations and apply the one which has cheaper routing lenght
    
    a_route1 = route_1_half_1.merge(route_2_half_2)
    a_route2 = route_1_half_2.merge(route_2_half_1)

    b_route1 = route_1_half_1.merge(route_2_half_1)
    b_route2 = route_1_half_2.merge(route_2_half_2)

    cost_a = a_route1.length + a_route2.length
    cost_b = b_route1.length + b_route2.length

    # add the new routes depending on which combination is cheaper
    if cost_a < cost_b:
        res_r1 = a_route1
        res_r2 = a_route2
    else:
        res_r1 = b_route1
        res_r2 = b_route2

    cnt = 0     # how many routes were added
    if day.add_route(res_r1):
        cnt += 1
    if day.add_route(res_r2):
        cnt += 1

    delta_cost += (res_r1.evaluate(solution.vehicle) + res_r1.evaluate(solution.vehicle))
    return delta_cost, route_1, route_2, cnt

def undo_op3(solution, route_1, route_2, routes_added):
    
    day = route_1.day
    # remove last 2 or 1 routes
    for i in range(routes_added):
        day.remove_route(route_id = -1)
    
    day.add_route(route_1)
    day.add_route(route_2)

# ? operator 4
#   - take a task u and move it to a different route within the same day
#   - consider all spots in 1 route where it can be put in - think I can use binary search here
#   - or an alternative to consider only adding it at the end/beginning of a route, but try it for all routes
def op4(solution, edge_1_id, edge_2_id, route_1, route_2):

    # move edge_1 from route_1 before edge_2 in route_2

    if route_1.day.number != route_2.day.number:
        # routes in different days
        return None
    
    
    delta_cost -= (route_1.evaluate(solution.vehicle) + route_2.evaluate(solution.vehicle))

    edge_1 = route_1.targets[edge_1_id]


    # note - allowing the routes to be the same, ie to move the edge in the same route just a different place in it

    # remove edge in route 1
    route_1.remove_edge(pos = edge_1_id)
    # insert the edge before edge_2 in route_2
    route_2.insert_edge(edge_1, pos = edge_2_id)

    delta_cost += (route_1.evaluate(solution.vehicle) + route_2.evaluate(solution.vehicle))
    
    return delta_cost

def undo_op4(solution, edge_1_id, edge_2_id, route_1, route_2):
    op4(solution, edge_2_id, edge_1_id, route_2, route_1)
    day = route_1.day
    if route_1 not in day.routes:
        day.add_route(route_1)


# ? operator 5
#   - similar to op4, but take 2 successive tasks performed one after another and move them together as a sequence
#   - again consider all possible places
def op5(solution, edge_a1_id, edge_a2_id, edge_b_id, route_a, route_b):
    # take successive edges edge_a1, edge_a2 from route A and insert them before edge_b of route B
    
    if route_a.day.number != route_b.day.number:
        # only done between rotues in the same day
        return None
    
    delta_cost -= (route_a.evaluate(solution.vehicle) + route_b.evaluate(solution.vehicle))

    edge_a1 = route_a.targets[edge_a1_id]
    edge_a2 = route_a.targets[edge_a2_id]

    route_a.remove_edge(pos = edge_a2_id)
    route_a.remove_edge(pos = edge_a1_id)

    # b
    route_b.insert_edge(edge_a2, pos = edge_b_id)
    # a2 b
    route_b.insert_edge(edge_a1, pos = edge_b_id)
    # a1 a2 b
    
    delta_cost += (route_a.evaluate(solution.vehicle) + route_b.evaluate(solution.vehicle))


    return delta_cost


def undo_op5(solution, edge_a1_id, edge_a2_id, edge_b_id, route_a, route_b):
    op4(solution, edge_b_id, edge_a1_id, route_b, route_a)
    op4(solution, edge_b_id, edge_a2_id, route_b, route_a)

    day = route_a.day
    if route_a not in day.routes:
        day.add_route(route_a)

# ? operator 6
#   - remove a single service of an edge on some day
def op6(solution, d1, edge):

    if d1 not in edge.service_days:
        # can't remove a service if it isn't serviced on that day
        return None

    solution.days[d1].remove_edge(edge)
    edge.service_days.remove(d1)
    edge.service_days.sort()

    return True

def undo_op6(solution, d1, edge):
    op7(solution, d1, edge)

# ? operator 7
#   - add a single service of an edge on a day
#   - only if the edge is not already serviced on that day
def op7(solution, d1, edge):

    if d1 not in solution.get_work_days():
        # don't add services to a non-work day (weekend)
        return None
    elif d1 in edge.service_days:
        # if the edge is already serviced in that day
        return None
    
    solution.days[d1].add_edge(edge)
    # with the spacing penalty - the proper day will have more priority
    edge.service_days.append(d1)
    edge.service_days.sort()


    return True

def undo_op7(solution, d1, edge):
    op6(solution, d1, edge)
    solution.days[d1].recalculate_routes()

def run(solution):

     
    no_improvement_count = 0
    patience = 10       # how many iterations to go without improvement

    current_best_solution = solution

    original_score = current_best_solution.evaluate()
    best_before_score = original_score
    best_score = best_before_score
    
    iteration_count = 0
    iteration_start_time = 0
    iteration_end_time = 0
    iteration_time_taken = 0
    average_iteration_time = 0

 
    improving = True
    phase_improving = False
    while improving:
        improving = False

        iteration_count += 1
        iteration_start_time = time.time()

        # phase 1 - add or remove services of edges with too litle or too many services
        best_score, current_best_solution, phase_improving = phase_1(current_best_solution, best_score)

        p1_end_time = time.time()
        if iteration_count == 1:
            print(f"Phase 1 ended after {p1_end_time - iteration_start_time} seconds")
            print(f"Current score: {best_score}")

        if phase_improving:
            improving = True

        # phase 2 - move services from 1 day to another day and swap service days of edges with same frequency 
        best_score, current_best_solution, phase_improving = phase_2(current_best_solution, best_score)

        p2_end_time = time.time()
        if iteration_count == 1:
            print(f"Phase 2 ended after {p2_end_time - p1_end_time} seconds")
            print(f"Current score: {best_score}")

        if phase_improving:
            improving = True

        # phase 3 - improve the routes
        best_score, current_best_solution, phase_improving = phase_3(current_best_solution, best_score)

        if phase_improving:
            improving = True

        iteration_end_time = time.time()
        if iteration_count == 1:
            print(f"Phase 3 ended after {iteration_end_time - p2_end_time} seconds")
            print(f"Current score: {best_score}")
        

        iteration_time_taken = iteration_end_time - iteration_start_time
        average_iteration_time = average_iteration_time * (iteration_count - 1) / iteration_count + iteration_time_taken / iteration_count
        if iteration_count % 10 == 1:
            print(f"Iteration count: {iteration_count} iterations")
            print(f"Last iteration time: {iteration_time_taken} seconds")
            print(f"Iteration average time: {iteration_time_taken} seconds")
            print(f"Current score: {best_score}")
        
    print(f"Local search ended after {iteration_count} iterations.")
    print(f"Last iteration time: {iteration_time_taken} seconds")
    print(f"Iteration average time: {iteration_time_taken} seconds")
    print(f"Original score: {original_score}")
    print(f"Current score: {best_score}")

    return best_score, current_best_solution

def evaluate_neighbour(neighbour_solution, best_score, current_best_solution):
    neighbour_score = neighbour_solution.evaluate()
    improved = False
    if neighbour_score < best_score:
        best_score = neighbour_score
        current_best_solution = copy.deepcopy(neighbour_solution)
        improved = True
    return best_score, current_best_solution, improved


def phase_1(current_best_solution, best_score):
    # apply ops 6 and 7 - while you can get an improvement

    original_score = best_score

    working = current_best_solution

    work_days = set(working.get_work_days())

    improved = True
    improved_op = False

    while improved:
        improved = False

        over_satisfied_edges = working.get_over_satisfied_edges()


        for edge in over_satisfied_edges:
            for day in edge.service_days:
                if op6(working, day, edge):
                    best_score, current_best_solution, improved_op  = evaluate_neighbour(working, best_score, current_best_solution)
                    undo_op6(working, day, edge)
                    if improved_op:
                        improved = True

        under_satisfied_edges = working.get_under_satisfied_edges()
        for edge in under_satisfied_edges:

            no_service_days = work_days.difference(set(edge.service_days))
            for day in no_service_days:
                if op7(working, day, edge):
                    best_score, current_best_solution, improved_op = evaluate_neighbour(working, best_score, current_best_solution)
                    undo_op7(working, day, edge)
                    if improved_op:
                        improved = True

        # after trying all combinations save the best one and try again
        working = current_best_solution

    return best_score, current_best_solution, best_score < original_score


def phase_2(current_best_solution, best_score):
    # apply op 1 and op2 - while you can get an improvement

    original_score = best_score

    working = current_best_solution

    work_days = set(working.get_work_days())
    frequency_buckets = working.frequency_buckets

    improved = True
    improved_op = False
    while improved:
        improved = False

        # op1 - move a service from 1 day to another day
        # iterate through service days of an edge and opposite for moving to another day
        for edge in working.demanded_edges:

            no_service_days = work_days.difference(set(edge.service_days))

            for day_1 in edge.service_days:
                for day_2 in no_service_days:
                    if op1(working, day_1, day_2, edge):
                        best_score, current_best_solution, improved_op = evaluate_neighbour(working, best_score, current_best_solution)
                        undo_op1(working, day_1, day_2, edge)
                        if improved_op:
                            improved = True

        # op2 - swap the service days of 2 edges with the same frequency
        for bucket in frequency_buckets.values():
            for i in range(len(bucket)):
                edge_1 = bucket[i]
                for j in range(i+1, len(bucket)):
                    edge_2 = bucket[j]
                    if op2(working, edge_1, edge_2):
                        best_score, current_best_solution, improved_op = evaluate_neighbour(working, best_score, current_best_solution)
                        undo_op2(working, edge_1, edge_2)
                        if improved_op:
                            improved = True
                    # if is kinda pointless now, but still leaving it this way
                    


        working = current_best_solution

    return best_score, current_best_solution, best_score < original_score


def phase_3(current_best_solution, best_score):
    # apply ops 3, 4 and 5 - while you can get an improvement
    # for each day pick the best and apply it
    # can parallelize for each day separate thread

    original_score = best_score

    working = current_best_solution
    working_score = best_score
    

    work_days = working.get_work_days()

    improved = True

    while improved:
        improved = False

        for day in work_days:

            for i_count, route_1 in enumerate(working.day[day].routes):
 
                for r1_cutpoint in range(len(route_1.targets)):

                    # if you can take 2 successive edges - only not reached the last point
                    can_do_op5 = (r1_cutpoint + 1) < len(route_1.targets) 

                    for j_count, route_2 in enumerate(working.day[day].routes):
                        if i_count == j_count:
                            continue


                        # op4 and op5 perform work on all ordered pair of routes 
                        # but op3 performs work on all unordered pair of routes
                        # that's why counters i_count and j_count

                        can_do_op3 = i_count < j_count
                        for r2_cutpoint in range(len(route_2.targets)):

                            # op3
                            if can_do_op3:
                                res = op3(working, route_1, route_2, r1_cutpoint, r2_cutpoint)
                                if res is None:
                                    continue
                                else:
                                    delta_cost, route_1, route_2, cnt = res
                                    neighbour_score = working_score + delta_cost
                                    if neighbour_score < best_score :
                                        best_score = neighbour_score
                                        current_best_solution = copy.deepcopy(working)
                                        improved = True
                                    undo_op3(working, route_1, route_2, cnt)

                            # op4
                            delta_cost = op4(working, r1_cutpoint, r2_cutpoint, route_1, route_2)
                            if delta_cost is not None:
                                neighbour_score = working_score + delta_cost
                                if neighbour_score < best_score:
                                    best_score = neighbour_score
                                    current_best_solution = copy.deepcopy(working)
                                undo_op4(working, r1_cutpoint, r2_cutpoint, route_1, route_2)

                            # op5
                            if can_do_op5:
                                delta_cost = op5(working, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
                                if delta_cost is not None:
                                    neighbour_score = working_score + delta_cost
                                    if neighbour_score < best_score:
                                        best_score = neighbour_score
                                        current_best_solution = copy.deepcopy(working)
                                        improved = True
                                    undo_op5(working, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
                                

            # apply the best op for each day, since operations applied on different days don't have an effect on each other
            working = current_best_solution
            working_score = best_score

    return best_score, current_best_solution, best_score < original_score