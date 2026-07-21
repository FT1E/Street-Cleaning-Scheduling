

import heapq as hq


def run(demanded_edge_list, vehicle):

    hq.heapify(demanded_edge_list)

    day_assignment = [[] for _ in range(vehicle['planning_duration'])]
    capacity_used = [0] * vehicle['planning_duration']

    next_day_streets = [[] for _ in range(vehicle['planning_duration'] + 1)]


    for day in range(vehicle['planning_duration']):

        demanded_edge_list = demanded_edge_list + next_day_streets[0]

        for i in range(vehicle['planning_duration'] - day - 1):
            next_day_streets[i] = next_day_streets[i+1]

        if day + 1 in vehicle['days_no_service']:
            # skip day if vehicle not available for today
            continue

        hq.heapify(demanded_edge_list)
            

        while capacity_used[day] < vehicle['count'] * vehicle['capacity'] and len(demanded_edge_list) > 0:
            
            # get edge with nearest deadline
            edge = hq.heappop(demanded_edge_list)

            if capacity_used[day] + edge.demand > vehicle['count'] * vehicle['capacity']:
                # if edge has higher demand than the vehicle can handle for the day then skip it for today
                hq.heappush(next_day_streets[0], edge)
                continue

            capacity_used[day] += edge.demand
            day_assignment[day].append(edge)
            edge.set_cleaning_day(day)


            if (edge.last_cleaning_day + edge.freq) < vehicle['planning_duration']:
                # push it to the future for at least freq/2 days
                # so some edgees that have higher frequency aren't clean
                hq.heappush(next_day_streets[int(edge.freq // 2)], edge)

    return day_assignment, capacity_used