from enum import Enum

from models.knapsack import Knapsack
from typing import List


class State:
    def __init__(self, knapsack: Knapsack, bit_combination: List[int]):
        self.knapsack = knapsack
        self.bit_combination = bit_combination

    @property
    def solution_weight(self):
        return sum(
            self.knapsack.items_list[item_index].weight
            for item_index, bit in enumerate(self.bit_combination) if bit == 1
        )

    @property
    def solution_price(self):
        return sum(
            self.knapsack.items_list[item_index].price
            for item_index, bit in enumerate(self.bit_combination) if bit == 1
        )

    def switch_bit_at_position(self, position: int):
        # toggle bit
        self.bit_combination[position] ^= 1

    def better(self, other_state) -> bool:
        return self.solution_price > other_state.solution_price

    def is_valid(self) -> bool:
        return self.solution_weight <= self.knapsack.capacity
