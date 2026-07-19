
import random
import copy
import sys

sys.path.append('..')

from util.routing_heuristic import Route

# * receives an sp-carp solution, on which it performs local search

# task = serviced edge

# ? operator 1:
#   - take a task u on day i and move it from day i (d1) to day j (d2)
#   !- make sure to pick day d2 so that the edge is not already serviced that day - see below op1_alt comments
def op1(solution, d1, d2, e_id):
    # e_id is index of edge in day.edges

    edge = solution.days[d1].remove_edge(edge_id = e_id)

    if edge is None:
        return None
    
    if d2 in edge.service_days:
        return
    
    solution.days[d2].add_edge(edge)

    edge.service_days.remove(d1)
    edge.service_days.append(d1)
    edge.service_days.sort()

# ? alternate operator 1
#   - take a task u from day i (d1) and move it a couple days before or after to satisfy the spacing between services wrt frequency
#   - kinda finding an alternative solution to service_days, such that the difference of any 2 consecutive numbers is less than the frequency
def op1_alt(solution, d1, e_id):
    # todo
    pass

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

    cut1 = random.randint(1, len(r1.targets) - 2)
    cut2 = random.randint(1, len(r2.targets) - 2)

    r1_h1 = Route(r1.targets[:cut1])
    r1_h2 = Route(r1.targets[cut1:])

    r2_h1 = Route(r2.targets[:cut2])
    r2_h2 = Route(r2.targets[cut2:])

    print(r1_h1)
    print(r1_h2)
    print(r2_h1)
    print(r2_h2)
    
    a_r1 = r1_h1.merge(r2_h2)
    a_r2 = r1_h2.merge(r2_h1)

    b_r1 = r1_h1.merge(r2_h1)
    b_r2 = r1_h2.merge(r2_h2)

    cost_a = a_r1.length + a_r2.length
    cost_b = b_r1.length + b_r2.length

    # add the new routes depending on which combination is cheaper
    if cost_a < cost_b:
        day.add_route(a_r1)
        day.add_route(a_r2)
    else:
        day.add_route(b_r1)
        day.add_route(b_r2)

# ? operator 4
#   - similar to operator 1 but do it within a day
#   - take 2 random tasks u and v and move u to be serviced after v or before u
#   - just make sure it's different, like don't take 2 (u,v) and move u before v which already is
#   - different from (u, x, v) and move u before v to get (x, u, v)
def op4(solution):
    pass





def run(solution):

    n1 = copy.deepcopy(solution)
    
    work_days = n1.get_work_days()
    d1, d2 = random.sample(work_days, 2)
    edge_id = random.randint(0, len(n1.days[d1].edges) - 1)

    selected_edge = n1.days[d1].edges[edge_id]
    
    op1(n1, d1, d2, edge_id)


    n2 = copy.deepcopy(solution)
    n2_edge1, n2_edge2 = op2(n2)

    n3 = copy.deepcopy(solution)
    op3(n3)

    # print("ORIGINAL SOLUTION")
    # print('-' * 50)
    # print(' ' * 50)
    # print('-' * 50)
    # solution.print()
    
    # print("NEIGHBOUR 3 SOLUTION")
    # print('-' * 50)
    # print(' ' * 50)
    # print('-' * 50)
    # n2.print()

    # print('-' * 50)
    # print(' ' * 50)
    # print('-' * 50)

    # print('\n\n')
    # print(len(n1.days[d1].edges))
    # print(d1, d2, edge_id)
    # print(selected_edge)

    # print('\n\nSelected edges')
    # print(n2_edge1)
    # print(n2_edge2)

    print(f"\n\nOriginal solution cost: {solution.evaluate()}")
    print(f"Neighbouring (op3) solution cost: {n3.evaluate()}")
    
    
    no_improvement_count = 0
    patience = 10       # how many iterations to go without improvement
    

