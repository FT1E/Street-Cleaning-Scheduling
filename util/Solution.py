
# class(es) for representing a solution
# performing changes on it
# evaluating how good it is

# Hierarchy
#   - each solution contains days
#   - each day contains trips routes for it
#   - each route contains a sequence of required edges to traverse

class Solution:

    # self.day_assignments[i] = routes for day i
    # self.work_day[i] = true if i is a work day, else false - depends on vehicle

    def __init__(self, day_assignments):
        self.day_assignments = day_assignments
        self.work_day = [True for x in day_assignments if len(x) > 0 else False]
        pass


    # ! careful for out of bounds exceptions for below methods
    def get_day_routes(self, day):
        return self.day_assignments[day]

    def get_day_route_count(self, day):
        return len(self.day_assignments[day])

    def get_day_route(self, day, route):
        return self.day_assignments[day][route]



    # todo - operators for getting a neigbouring solution