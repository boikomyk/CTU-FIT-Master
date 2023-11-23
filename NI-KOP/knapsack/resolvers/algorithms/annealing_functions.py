from enum import Enum

from models.knapsack import Knapsack
from resolvers.algorithms.state import State

import random

from resolvers.problem_resolvers import Resolver


class InitialStateGenerator(Enum):
    empty = 1   # empty knapsack
    random = 2  # random filled knapsack
    greedy = 3  # knapsack filled by greedy


class AnnealingFunctions:
    @staticmethod
    def generate_state_empty(knapsack: Knapsack):
        return State(
            knapsack=knapsack,
            bit_combination=[0]*knapsack.get_items_cnt()
        )

    @staticmethod
    def generate_state_by_random(knapsack: Knapsack) -> State:
        return State(
            knapsack=knapsack,
            bit_combination=[random.randint(0, 1) for item_index in range(knapsack.get_items_cnt())]
        )

    @staticmethod
    def generate_state_by_greedy(knapsack: Knapsack) -> State:
        _, greedy_solution = Resolver.greedy(knapsack)

        return State(
            knapsack=knapsack,
            bit_combination=greedy_solution.bit_combination
        )
