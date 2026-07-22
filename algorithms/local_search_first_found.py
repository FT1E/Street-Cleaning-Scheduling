

import time
import copy
import sys

sys.path.append('..')

from algorithms.local_search import op1, undo_op1
from algorithms.local_search import op2, undo_op2
from algorithms.local_search import op3, undo_op3
from algorithms.local_search import op4, undo_op4
from algorithms.local_search import op5, undo_op5
from algorithms.local_search import op6, undo_op6
from algorithms.local_search import op7, undo_op7


def run(solution):
    work_days = solution.get_work_days()
    
    
    no_improvement_count = 0
    patience = 10       # how many iterations to go without improvement

    best_before_solution = solution     # best found before applying operators in this iteration
    current_best_solution = best_before_solution    # best found from applying operators during this iteration


    original_score = current_best_solution.evaluate()
    best_before_score = original_score
    best_score = best_before_score
    
    iteration_count = 0
    iteration_start_time = 0
    iteration_end_time = 0
    iteration_time_taken = 0
    average_iteration_time = 0

    op1_count = 0
    op2_count = 0
    op3_count = 0
    op4_count = 0
    op5_count = 0
    op6_count = 0
    op7_count = 0

    frequency_buckets = solution.frequency_buckets


    while no_improvement_count < patience:
        
        iteration_start_time = time.time()
        

        # 1. operators between days
        # 1.1 - op1 - move an edge from day i to day j - all combinations are tried, including both moving a service forward and backward
        for i in work_days:
            for j in work_days:
                if i == j:
                    continue
                for edge in solution.days[i].edges:
                    if op1(best_before_solution, i, j, edge):
                        best_score, current_best_solution, improved = evaluate_neighbour(best_before_solution, best_score, current_best_solution)
                        if not improved:
                            undo_op1(best_before_solution, i, j, edge)
                    if iteration_count == 1:
                        op1_count += 1
        

        # 1.2 - op2 - swapping the service days of 2 edges with the same frequency
        for bucket in frequency_buckets.values():
            # bucket == list of all edges with the same frequency
            for i in range(len(bucket)):
                edge_1 = bucket[i]
                for j in range(i+1, len(bucket)):
                    edge_2 = bucket[j]

                    if op2(best_before_solution, edge_1, edge_2):
                        best_score, current_best_solution, improved = evaluate_neighbour(best_before_solution, best_score, current_best_solution)
                        if not improved:
                            undo_op2(best_before_solution, edge_1, edge_2)
                    # if is kinda pointless now, but still leaving it this way
                    if iteration_count == 0:
                        op2_count += 1

        # 2. operators within days
        # 2.1
        #   - op3 - cut 2 routes and merge them - cuts can be at endpoints so it can be just merging 2 routes
        #   - op4 - move an edge from route 1 to a different route 2 - before an edge 2 inside it
        #   - op5 - similar to route 4, but instead of moving 1 edge, take 2 successive edges in the route and move them together


        # below counters are for op3 - since it operates on all unordered pair of routes in the same day
        # but op4, op5 operate on all ordered pair of routes
        i_count = 0
        j_count = 0

        neighbour_score = 0

        can_do_op5 = False
        for i in work_days:
            day = best_before_solution.days[i]
            
            i_count = 0
            for route_1 in day.routes:
                i_count += 1
                for r1_cutpoint in range(len(route_1.targets)):
                    can_do_op5 = r1_cutpoint < len(route_1.targets) - 1

                    j_count = 0
                    for route_2 in day.routes:
                        if i_count == j_count:
                            continue
                        j_count += 1

                        for r2_cutpoint in range(len(route_2.targets)):
                            
                            if i_count < j_count:
                                res = op3(best_before_solution, route_1, route_2, r1_cutpoint, r2_cutpoint)
                                if res is None:
                                    continue
                                else:
                                    delta_cost, route_1, route_2, cnt = res
                                    neighbour_score = best_before_score + delta_cost
                                    if neighbour_score < best_score :
                                        best_score = neighbour_score
                                        current_best_solution = copy.deepcopy(best_before_solution)
                                        break
                                    else:
                                        undo_op3(best_before_solution, route_1, route_2, cnt)

                                if iteration_count == 0:
                                    op3_count += 1

                            delta_cost = op4(best_before_solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
                            if delta_cost is not None:
                                neighbour_score = best_before_score + delta_cost
                                if neighbour_score < best_score:
                                    best_score = neighbour_score
                                    current_best_solution = copy.deepcopy(best_before_solution)
                                    break
                                else:
                                    undo_op4(best_before_solution, r1_cutpoint, r2_cutpoint, route_1, route_2)
                            if iteration_count == 0:
                                op4_count += 1

                            if can_do_op5:
                                delta_cost = op5(best_before_solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
                                if delta_cost is not None:
                                    neighbour_score = best_before_score + delta_cost
                                    if neighbour_score < best_score:
                                        best_score = neighbour_score
                                        current_best_solution = copy.deepcopy(best_before_solution)
                                        break
                                    else:
                                        undo_op5(best_before_solution, r1_cutpoint, r1_cutpoint + 1, r2_cutpoint, route_1, route_2)
                                
                                if iteration_count == 0:
                                    op5_count +=1 
                        else:
                            continue
                        break
                    else:
                        continue
                    break
                else:
                    continue
                break
            else:
                continue
            break

        
        # 2.2
        #   - op6 - remove a single service of an edge
        #   - op7 - add a single service of an edge
        
        unsatisfied_edges = best_before_solution.unsatisfied_edges()
        for edge in unsatisfied_edges:
            for i in work_days:
                
                if op6(best_before_solution, i, edge):
                    best_score, current_best_solution, improved = evaluate_neighbour(best_before_solution, best_score, current_best_solution)
                    if not improved:
                        undo_op6(best_before_solution, i, edge)

                if iteration_count == 0:
                    op6_count += 1

        oversatisfied_edges = best_before_solution.over_satisfied_edges()
        for edge in oversatisfied_edges:
            for i in work_days:
                if op7(best_before_solution, i, edge):
                    best_score, current_best_solution, improved = evaluate_neighbour(best_before_solution, best_score, current_best_solution)
                    if not improved:
                        undo_op7(best_before_solution, i, edge)
                    
                if iteration_count == 0:
                    op7_count += 1

        if best_score < best_before_score:
            best_before_score = best_score
            best_before_solution = current_best_solution

            no_improvement_count = 0
        else:
            no_improvement_count += 1
            break       # todo - remove this break once you implement a shaking procedure
        
        iteration_end_time = time.time()

        iteration_time_taken = iteration_end_time - iteration_start_time

        iteration_count += 1

        average_iteration_time = (average_iteration_time) * (iteration_count - 1) / iteration_count + iteration_time_taken / iteration_count
        print(f"Iteration {iteration_count} end, current state:")
        print(f"Original score: {original_score}")
        print(f"Current best score: {best_score}")
        print(f"Average iteration time: {average_iteration_time}")


        if iteration_count == 1:
            print("Operations performed counters:")
            print(f"op1: {op1_count}")
            print(f"op2: {op2_count}")
            print(f"op3: {op3_count}")
            print(f"op4: {op4_count}")
            print(f"op5: {op5_count}")
            print(f"op6: {op6_count}")
            print(f"op7: {op7_count}")

    print(f"End of local search, after {iteration_count} iterations!")
    print(f"Original score: {original_score}")
    print(f"Current best score: {best_score}")
    print(f"Average iteration time: {average_iteration_time}")

    return current_best_solution

def evaluate_neighbour(neighbour_solution, best_score, current_best_solution):
    neighbour_score = neighbour_solution.evaluate()
    improved = False
    if neighbour_score < best_score:
        best_score = neighbour_score
        current_best_solution = copy.deepcopy(neighbour_solution)
        improved = True
    return best_score, current_best_solution, improved