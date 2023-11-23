from enum import Enum
from typing import List

from models.item import Item


class ProblemType(Enum):
    CONSTRUCTIVE = 0
    DECISION = 1


class Knapsack:
    def __init__(self, id: int, items_cnt: int, capacity: int, min_req_price: int, problem_type: ProblemType):
        self.id = id
        self.items_cnt = items_cnt
        self.capacity = capacity
        self.min_req_price = min_req_price
        self.problem_type = problem_type
        self.items_list: List[Item] = list()

    def get_items_cnt(self):
        return len(self.items_list)

    def is_valid_knapsack(self, weight: int, price: int):
        # ___ CONSTRUCTIVE ___
        if self.problem_type == ProblemType.CONSTRUCTIVE:
            if weight <= self.capacity:
                return True

        # ___ DECISION ___
        elif self.problem_type == ProblemType.DECISION:
            if weight <= self.capacity and price >= self.min_req_price:
                return True
        return False
