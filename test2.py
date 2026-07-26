
from data.read_data import get_graph_demanded_edges, get_vehicle_data, get_graph_al, get_graph_edge_list
from algorithms.greedy_single import run as gs_run
from algorithms.greedy_dynamic_cluster import run as gdc_run
from algorithms.greedy_fixed_cluster import run as gfc_run

from solution_representation.Solution import Solution


from algorithms.local_search_first_found import run as ls_run

from algorithms.local_search import op1, undo_op1
from algorithms.local_search import op2, undo_op2
from algorithms.local_search import op3, undo_op3
from algorithms.local_search import op4, undo_op4
from algorithms.local_search import op5, undo_op5
from algorithms.local_search import op6, undo_op6
from algorithms.local_search import op7, undo_op7
from algorithms.local_search import evaluate_neighbour
from algorithms.local_search import phase_3
import random


import copy
import time

GRAPH_ID = 0
VEHICLE_ID = 0


# todo - remove demanded edges with frequency higher than planning period, or just make them zero-demand edges

vehicle = get_vehicle_data(VEHICLE_ID)

# ! below for debugging
# vehicle['distance_limit'] = 500     
# print(f"Vehicle distance limit: {vehicle['distance_limit']}")
# vehicle['planning_duration'] = 7
vehicle['count'] = 50           # ? playing around with this value so it's not too high, but also not too low so some edges don't get serviced at all
# (graph_id, vehicle_id) >= value so that no edge is ignored (not serviced at all)
# (0, 0) >= 33



demanded_edges = get_graph_demanded_edges(GRAPH_ID, filter = vehicle['planning_duration'])
adjacency_list = get_graph_al(GRAPH_ID)


# print(vehicle)
# day_assignments, capacity_used = gs_run(demanded_edges, vehicle)
day_assignments, capacity_used =    gdc_run(demanded_edges, adjacency_list, vehicle)
# day_assignments, capacity_used = gfc_run(demanded_edges, adjacency_list, vehicle, GRAPH_ID)



solution = Solution(day_assignments, demanded_edges, adjacency_list, vehicle, GRAPH_ID)

# print('Printing solution ...')
# print(solution)

eval_start_t = time.time()
cost = solution.evaluate()
eval_end_t = time.time()

eval_time = eval_end_t - eval_start_t

print(f"Solution cost: {cost}")

unsatisfied_edges = solution.unsatisfied_edges()

print(f"Number of all demanded edges: {len(demanded_edges)}")
print(f"Number of unsatisfied edges: {len(unsatisfied_edges)}")

# for edge in unsatisfied_edges:
#     print(edge)
#     print(f'\t{edge.service_days}')


print(f"Expected number of total services: {solution.expected_number_of_services()}")
print(f"Actual number of total services: {solution.total_number_of_services()}")


# solution.checking_references()

# ls_run(solution)


def op1_checker(solution, day_1, day_2, edge):

    # print("OP1 REFERENCE CHECKS")
    # print("BEFORE")
    # print(f"Selected edge: {edge}")
    # print(f"\tEdge service days: {edge.service_days}")
    # print(f"Day 1: {day_1}")
    # print(f"Day 2: {day_2}")
    # print(f"\tIs edge in day 1: {solution.days[day_1].edge_in_day(edge)}")
    # print(f"\tIs edge in day 2: {solution.days[day_2].edge_in_day(edge)}")

    before_sd = edge.service_days[:]

    before_check = solution.days[day_1].edge_in_day(edge) and not solution.days[day_2].edge_in_day(edge)

    start_time = time.time()
    route, route_pos = op1(solution, day_1, day_2, edge)
    end_time = time.time()
    op1_time = end_time - start_time


    after_check = not solution.days[day_1].edge_in_day(edge) and solution.days[day_2].edge_in_day(edge)
    
    after_sd = edge.service_days[:]

    # print("AFTER OP1 / BEFORE UNDO_OP1")
    # print(f"Selected edge: {edge}")
    # print(f"\tEdge service days: {edge.service_days}")
    # print(f"Day 1: {day_1}")
    # print(f"Day 2: {day_2}")
    # print(f"\tIs edge in day 1: {solution.days[day_1].edge_in_day(edge)}")
    # print(f"\tIs edge in day 2: {solution.days[day_2].edge_in_day(edge)}")

    check = before_check and after_check
    if not check:
        print(f"op1 time: {op1_time}")
        print(f"op1 correctness: {check}")
        print(f"{edge}")
        print(f"Before check: {before_check}")
        print(f"After check: {after_check}")
        print(f"Before service days: {before_sd}")
        print(f"Edge in day above: {[solution.days[d].edge_in_day(edge) for d in before_sd]}")
        print(f"After service days: {after_sd}")
        print(f"Edge in day above: {[solution.days[d].edge_in_day(edge) for d in after_sd]}")
        print()

    return route, route_pos


def undo_op1_checker(solution, day_1, day_2, edge, route, route_pos):

    # print("AFTER OP1 / BEFORE UNDO_OP1")
    # print(f"Selected edge: {edge}")
    # print(f"\tEdge service days: {edge.service_days}")
    # print(f"Day 1: {day_1}")
    # print(f"Day 2: {day_2}")
    # print(f"\tIs edge in day 1: {solution.days[day_1].edge_in_day(edge)}")
    # print(f"\tIs edge in day 2: {solution.days[day_2].edge_in_day(edge)}")



    before_sd = edge.service_days[:]

    before_check = not solution.days[day_1].edge_in_day(edge) and solution.days[day_2].edge_in_day(edge)


    pass
    start_time = time.time()
    undo_op1(solution, day_1, day_2, edge, route, route_pos)
    end_time = time.time()

    undo_op1_time = end_time - start_time

    after_check = solution.days[day_1].edge_in_day(edge) and not solution.days[day_2].edge_in_day(edge)
    
    after_sd = edge.service_days[:]





    # print('\n\n')
    # print("AFTER UNDO_OP1")
    # print(f"Selected edge: {edge}")
    # print(f"\tEdge service days: {edge.service_days}")
    # print(f"Day 1: {day_1}")
    # print(f"Day 2: {day_2}")
    # print(f"\tIs edge in day 1: {solution.days[day_1].edge_in_day(edge)}")
    # print(f"\tIs edge in day 2: {solution.days[day_2].edge_in_day(edge)}")

    # print('\n\n')

    check = before_check and after_check
    if not check:
        print(f"undo_op1 time: {undo_op1_time}")
        print(f"undo_op1 correctness: {check}")
        print(f"{edge}")
        print(f"Before check: {before_check}")
        print(f"After check: {after_check}")
        print(f"Before service days: {before_sd}")
        print(f"Edge in day above: {[solution.days[d].edge_in_day(edge) for d in before_sd]}")
        print(f"After service days: {after_sd}")
        print(f"Edge in day above: {[solution.days[d].edge_in_day(edge) for d in after_sd]}")
        print()


CORRECT_COUNT = 0
def op2_checker(solution, edge_1, edge_2):

    global CORRECT_COUNT
    
    # print("OP2 REFERENCE CHECKS")
    # print("BEFORE")
    # print(f"Selected edge 1: {edge_1}")
    # print(f"\tEdge 1 service days: {edge_1.service_days}")
    # print(f"\tIs edge 1 in day:")
    # print([solution.days[d].edge_in_day(edge_1) for d in edge_1.service_days])
    # print(f"Selected edge 2: {edge_2}")
    # print(f"\tEdge 2 service days: {edge_2.service_days}")
    # print(f"\tIs edge 2 in day:")
    # print([solution.days[d].edge_in_day(edge_2) for d in edge_2.service_days])
    # print(f"ALL DAYS CHECK: {all_days}")
    # print(f"Edge 1: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
    # print(f"Edge 2: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")

    # print('\n\nOP2 START\n')

    e1_before_sd = edge_1.service_days[:]
    e2_before_sd = edge_2.service_days[:]

    all_days = list(set(edge_1.service_days[:] + edge_2.service_days[:]))
    all_days.sort()

    before_e1_check = True
    for d in e1_before_sd:
        if not solution.days[d].edge_in_day(edge_1):
            before_e1_check = False

    before_e2_check = True
    for d in e2_before_sd:
            if not solution.days[d].edge_in_day(edge_2):
                before_e2_check = False

    before_check = before_e1_check and before_e2_check        

    pass

    start_time = time.time()
    try:
        e1_routes, e2_routes = op2(solution, edge_1, edge_2)
    except Exception as e:
        print("Exception happenned in op2 with edges")
        print(edge_1)
        print(edge_2)
        print("Exception message:")
        print(e)
        
    end_time = time.time()

    op2_time = end_time - start_time


    # check edge_2 in edge_1 days
    after_e2_check = True
    for d in e1_before_sd:
        if not solution.days[d].edge_in_day(edge_2):
            after_e2_check = False

    # check edge_1 in edge_2 days
    after_e1_check = True
    for d in e2_before_sd:
        if not solution.days[d].edge_in_day(edge_1):
            after_e1_check = False

    after_check = after_e1_check and after_e2_check        

    check = before_check and after_check

    # print("AFTER")
    # print(f"Selected edge 1: {edge_1}")
    # print(f"\tEdge 1 service days: {edge_1.service_days}")
    # print(f"\tIs edge 1 in day:")
    # print([solution.days[d].edge_in_day(edge_1) for d in edge_1.service_days])
    # print(f"Selected edge 2: {edge_2}")
    # print(f"\tEdge 2 service days: {edge_2.service_days}")
    # print(f"\tIs edge 2 in day:")
    # print([solution.days[d].edge_in_day(edge_2) for d in edge_2.service_days])


    # print(f"ALL DAYS CHECK: {all_days}")
    # print(f"Edge 1: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
    # print(f"Edge 2: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")

    # print('\n\nUNDO_OP2 START\n')

    if not check:
        print(f"Correct count of op2 performed till now: {CORRECT_COUNT}")
        print(f"op2_time: {op2_time}")
        print(f"op2 correctness check: {check}")
        print(f"Before check: {before_check}")
        print(f"After check: {after_check}")
        print(f"Edge 1: {edge_1}")
        print(f"\tBefore service days: {e1_before_sd}")
        print(f"\tAfter service days: {edge_1.service_days}")
        print(f"Edge 2: {edge_2}")
        print(f"\tBefore service days: {e2_before_sd}")
        print(f"\tAfter service days: {edge_2.service_days}")
        print(f"All days: {all_days}")
        print(f"Edge 1 in day (for all_days) check: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
        print(f"Edge 2 in day (for all_days) check: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")
        print()
    else:
        CORRECT_COUNT += 1

    return e1_routes, e2_routes

def undo_op2_cheker(solution, edge_1, edge_2, e1_routes, e2_routes):

    # print("UNDO_OP2 REFERENCE CHECKS")
    # print("BEFORE")
    # print(f"Selected edge 1: {edge_1}")
    # print(f"\tEdge 1 service days: {edge_1.service_days}")
    # print(f"\tIs edge 1 in day:")
    # print([solution.days[d].edge_in_day(edge_1) for d in edge_1.service_days])
    # print(f"Selected edge 2: {edge_2}")
    # print(f"\tEdge 2 service days: {edge_2.service_days}")
    # print(f"\tIs edge 2 in day:")
    # print([solution.days[d].edge_in_day(edge_2) for d in edge_2.service_days])


    # print(f"ALL DAYS CHECK: {all_days}")
    # print(f"Edge 1: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
    # print(f"Edge 2: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")

    # print('\n\nUNDO_OP2 START\n')

    e1_before_sd = edge_1.service_days[:]
    e2_before_sd = edge_2.service_days[:]

    all_days = list(set(edge_1.service_days[:] + edge_2.service_days[:]))
    all_days.sort()

    before_e1_check = True
    for d in e1_before_sd:
        if not solution.days[d].edge_in_day(edge_1):
            before_e1_check = False

    before_e2_check = True
    for d in e2_before_sd:
            if not solution.days[d].edge_in_day(edge_2):
                before_e2_check = False

    before_check = before_e1_check and before_e2_check        


    pass
    start_time = time.time()
    undo_op2(solution, edge_1, edge_2, e1_routes, e2_routes)
    end_time = time.time()
    undo_op2_time = end_time - start_time


    # check edge_2 in edge_1 days
    after_e2_check = True
    for d in e1_before_sd:
        if not solution.days[d].edge_in_day(edge_2):
            after_e2_check = False

    # check edge_1 in edge_2 days
    after_e1_check = True
    for d in e2_before_sd:
        if not solution.days[d].edge_in_day(edge_1):
            after_e1_check = False

    after_check = after_e1_check and after_e2_check        

    check = before_check and after_check


    # print('\n\nUNDO_OP2 END\n')

    # print("AFTER")
    # print(f"Selected edge 1: {edge_1}")
    # print(f"\tEdge 1 service days: {edge_1.service_days}")
    # print(f"\tIs edge 1 in day:")
    # print([solution.days[d].edge_in_day(edge_1) for d in edge_1.service_days])
    # print(f"Selected edge 2: {edge_2}")
    # print(f"\tEdge 2 service days: {edge_2.service_days}")
    # print(f"\tIs edge 2 in day:")
    # print([solution.days[d].edge_in_day(edge_2) for d in edge_2.service_days])


    # print(f"ALL DAYS CHECK: {all_days}")
    # print(f"Edge 1: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
    # print(f"Edge 2: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")

    if not check:
        print("undo_op2 check is same as op2 check since it's symmetrical op\n")
        print(f"undo_op2 time: {undo_op2_time}")
        print(f"undo_op2 correctness: {check}")
        print(f"Before check: {before_check}")
        print(f"After check: {after_check}")
        print(f"Edge 1: {edge_1}")
        print(f"\tBefore service days: {e1_before_sd}")
        print(f"\tAfter service days: {edge_1.service_days}")
        print(f"Edge 2: {edge_2}")
        print(f"\tBefore service days: {e2_before_sd}")
        print(f"\tAfter service days: {edge_2.service_days}")
        print(f"All days: {all_days}")
        print(f"Edge 1 in day (for all_days) check: {[solution.days[d].edge_in_day(edge_1) for d in all_days]}")
        print(f"Edge 2 in day (for all_days) check: {[solution.days[d].edge_in_day(edge_2) for d in all_days]}")
        print()




print(f"\n\nTime it took for 1 evaluate: {eval_time} seconds")

# edge = random.choice(solution.demanded_edges)
# day_1 = random.choice(edge.service_days)
# no_service_days = (set(solution.get_work_days())).difference(edge.service_days)
# day_2 = random.choice(list(no_service_days))










# edge_1, edge_2 = random.sample(random.choice(list(solution.frequency_buckets.values())), 2)

# while edge_1.service_days == edge_2.service_days:
#     edge_1, edge_2 = random.sample(random.choice(list(solution.frequency_buckets.values())), 2)

# if edge_1 is None:
#     print("Random sample on freq buckets not working")

# all_days = list(set(edge_1.service_days + edge_2.service_days))
# all_days.sort()












# start_time = time.time()
# route, route_pos = op6(solution, day_1, edge)
# end_time = time.time()

# op6_time = end_time - start_time


# start_time = time.time()
# undo_op6(solution, day_1, edge, route, route_pos)
# end_time = time.time()

# undo_op6_time = end_time - start_time


# start_time = time.time()
# op7(solution, day_2, edge)
# end_time = time.time()

# op7_time = end_time - start_time


# start_time = time.time()
# undo_op7(solution, day_1, edge)
# end_time = time.time()

# undo_op7_time = end_time - start_time

# day_1 = day_1


# route_1, route_2 = random.sample(solution.days[day_1].routes, 2)

# while len(route_1.targets) <= 1:
#     route_1, route_2 = random.sample(solution.days[day_1].routes, 2)

# r1_cutpoint = random.randint(0, len(route_1.targets) - 2)
# r2_cutpoint = random.randint(0, len(route_2.targets) - 1)


# start_time = time.time()
# res = op3(solution, route_1, route_2, r1_cutpoint, r2_cutpoint)
# end_time = time.time()

# op3_time = end_time - start_time

# delta_cost, route_1_undo, route_2_undo, cnt = res

# start_time = time.time()
# undo_op3(solution, route_1_undo, route_2_undo, cnt)
# end_time = time.time()

# undo_op3_time = end_time - start_time

# start_time = time.time()
# op4(solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
# end_time = time.time()

# op4_time = end_time - start_time

# start_time = time.time()
# undo_op4(solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
# end_time = time.time()

# undo_op4_time = end_time - start_time


# start_time = time.time()
# op5(solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
# end_time = time.time()

# op5_time = end_time - start_time


# start_time = time.time()
# undo_op5(solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
# end_time = time.time()

# undo_op5_time = end_time - start_time



# print("Time it took for a single performance of each operation")
# print(f"\nop1 Time:\t {op1_time:.10f} seconds")
# print(f"undo_op1 Time:\t {undo_op1_time:.10f} seconds")
# print(f"\nop2 Time:\t {op2_time:.10f} seconds")
# print(f"undo_op2 Time:\t {undo_op2_time:.10f} seconds")
# print(f"\nop3 Time:\t {op3_time:.10f} seconds")
# print(f"undo_op3 Time:\t {undo_op3_time:.10f} seconds")
# print(f"\nop4 Time:\t {op4_time:.10f} seconds")
# print(f"undo_op4 Time:\t {undo_op4_time:.10f} seconds")
# print(f"\nop5 Time:\t {op5_time:.10f} seconds")
# print(f"undo_op5 Time:\t {undo_op5_time:.10f} seconds")
# print(f"\nop6 Time:\t {op6_time:.10f} seconds")
# print(f"undo_op6 Time:\t {undo_op6_time:.10f} seconds")
# print(f"\nop7 Time:\t {op7_time:.10f} seconds")
# print(f"undo_op7 Time:\t {undo_op7_time:.10f} seconds")


def phase_2_checkers(current_best_solution, best_score):
    # apply op 1 and op2 - while you can get an improvement

    original_score = best_score

    working = current_best_solution

    work_days = set(working.get_work_days())

    iter_count = 0
    iter_avg_time = 0
    

    improved = True
    improved_op = False
    while improved:
        improved = False

        iter_start_time = time.time()
        iter_count += 1

        
        # op2 - swap the service days of 2 edges with the same frequency
        for bucket in working.frequency_buckets.values():
            for i in range(len(bucket)):
                edge_1 = bucket[i]
                for j in range(i+1, len(bucket)):
                    edge_2 = bucket[j]
                    res = op2_checker(working, edge_1, edge_2)
                    if res is not None:
                        edge_1_routes, edge_2_routes = res
                        best_score, current_best_solution, improved_op = evaluate_neighbour(working, best_score, current_best_solution)
                        undo_op2_cheker(working, edge_1, edge_2, edge_1_routes, edge_2_routes)
                        if improved_op:
                            improved = True
                    # if is kinda pointless now, but still leaving it this way
                    
        print("op2 iteration finished!")
        # op1 - move a service from 1 day to another day
        # iterate through service days of an edge and opposite for moving to another day
        for edge in working.demanded_edges:

            no_service_days = work_days.difference(set(edge.service_days))

            for day_1 in edge.service_days:
                for day_2 in no_service_days:
                    res =  op1_checker(working, day_1, day_2, edge)
                    if res is not None:
                        best_score, current_best_solution, improved_op = evaluate_neighbour(working, best_score, current_best_solution)

                        route, route_pos = res
                        undo_op1_checker(working, day_1, day_2, edge, route, route_pos)
                        if improved_op:
                            improved = True
        print("op1 iteration finished!")


        working = current_best_solution

        iter_end_time = time.time()
        
        iter_time = iter_end_time - iter_start_time
        iter_avg_time = iter_avg_time * (iter_count - 1) / iter_count + iter_time / iter_count

        print("Phase 2:")
        print(f"Iteration count: {iter_count} iterations")
        print(f"Last iteration time: {iter_time} seconds")
        print(f"Average iteration time: {iter_avg_time} seconds")
        print(f"Current best score: {best_score}")
        print('\n')
        

    print("Phase 2 Report:")
    print(f"Iteration count: {iter_count} iterations")
    print(f"Last iteration time: {iter_time} seconds")
    print(f"Average iteration time: {iter_avg_time} seconds")
    print(f"Current best score: {best_score}")
    print('\n\n')


    return best_score, current_best_solution, best_score < original_score


# best_score, best_solution = phase_2_checkers(solution, cost)
best_score, best_solution = phase_3(solution, cost)