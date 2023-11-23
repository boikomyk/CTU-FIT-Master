from typing import List


class SATReference:
    def __init__(self, id: str, optimal_weight: int, optimal_configuration: List[bool]):
        self.id = id
        self.optimal_weight = optimal_weight
        self.optimal_configuration = optimal_configuration
