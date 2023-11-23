from models.sat_problem import SATProblem
from typing import List


class SATSolution:
    def __init__(self,
                 sat_problem: SATProblem,
                 solution_configuration: List[bool],
                 solution_weight: int,
                 configurations_cnt: int,
                 weights_evolution_history: List[int],
                 temperatures_evolution_history: List[float],
                 costs_evolution_history: List[int]
                 ):
        self.sat_problem = sat_problem

        self.solution_configuration = solution_configuration
        self.solution_weight = solution_weight
        self.configurations_cnt = configurations_cnt

        self.weights_evolution_history = weights_evolution_history
        self.temperatures_evolution_history = temperatures_evolution_history
        self.costs_evolution_history = costs_evolution_history

        self.time_ms = 0.
        self.sat_reference = None
        self.error = 0.0

    def calculate_error(self):
        if self.sat_reference:
            # at least one of prices should be different from zero
            if self.solution_weight != 0 or self.sat_reference.optimal_weight != 0:
                # |solution_price - reference_price| / |max(solution_price, reference_price)|
                self.error = abs(self.solution_weight - self.sat_reference.optimal_weight) \
                             / abs(max(self.solution_weight, self.sat_reference.optimal_weight))

    def display_comparing_with_reference(self):
        if self.sat_reference:
            print('-' * 100)
            print(str(self.solution_weight), "  ", " ".join(
                [str((indx + 1)) if literal_evaluation else str(-(indx + 1)) for indx, literal_evaluation in
                 enumerate(self.solution_configuration)]
            ))
            print(str(self.sat_reference.optimal_weight), "  ", " ".join(
                [str(indx + 1) if literal_evaluation else str(-(indx + 1)) for indx, literal_evaluation in
                 enumerate(self.sat_reference.optimal_configuration)]
            ))
            print('-' * 100)
