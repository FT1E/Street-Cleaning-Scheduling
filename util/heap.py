
from enum import Enum


# * example of an edge structure
edge = {
    'EdgeNumber' : 17,
    'StartNodeNumber' : 17,
    'EndNodeNumber' : 17,
    'Cost' : 17,
    'Freq' : 17,
    'LastDayCleaned' : 0    # default value 0
}

# heap with custom elements 

priority_type = Enum('PriorityType', {'Frequency' : 0, 'Deadline' : 1})

class Heap:
    def __init__(self, day=0, priority_type=PriorityType.Frequency):
        self.heap = []
        self.day = day
        self.priority_type = priority_type

    def insert(self, edge):
        self.heap.append(edge)
        current = len(self.heap) - 1

        while current >= 0:
            parent = self.get_parent_index(current)

            # if current edge has bigger prio than parent
            if self.compare(self.heap[current], self.heap[parent]):
                self.heap[current], self.heap[parent] = self.heap[parent], self.heap[current]
                current = parent
            else:
                break

    def get_min(self):
        return self.heap[0]
    
    def remove_min(self):
        current = 0
        while True:
            left = self.get_left_child_index(current)
            right = self.get_right_child_index(current)

            if left >= len(self.heap):
                self.heap[current], self.heap[-1] = self.heap[-1], self.heap[current]
                self.heap.pop()
                break
            elif right >= len(self.heap):
                self.heap[current], self.heap[left] = self.heap[left], self.heap[current]
                self.heap.pop()
                break
            else:
                if self.compare(self.heap[left], self.heap[right]):
                    self.heap[current], self.heap[left] = self.heap[left], self.heap[current]
                    current = left
                else:
                    self.heap[current], self.heap[right] = self.heap[right], self.heap[current]
                    current = right
            

    def extract_min(self):
        min = self.get_min()
        self.remove_min()
        return min
    
    def get_parent_index(self, index):
        return (index - 1) // 2
    
    def get_left_child_index(self, index):
        return 2 * index + 1
    
    def get_right_child_index(self, index):
        return 2 * index + 2
        
    def compare(self, e1, e2):
        if(priority_type == PriorityType.Deadline):
            return (e1.Freq - self.day + e1.LastDayCleaned) < (e2.Freq - self.day + e2.LastDayCleaned)
        else:
            return e1.Freq < e2.Freq
        
    def set_day(self, day):
        self.day = day

    def set_priority_type(self, priority_type):
        self.priority_type = priority_type
