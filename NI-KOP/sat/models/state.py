from models.sat_problem import SATProblem
from typing import List


class State:
    def __init__(self, sat_problem: SATProblem, configuration: List[bool] = None):
        self.sat_problem = sat_problem
        self.configuration = configuration

    def switch_literal_evaluation_at_position(self, position: int):
        # toggle bit
        self.configuration[position] = not self.configuration[position]

    def is_valid(self) -> bool:
        return self.sat_problem.is_solution(self.configuration)

    def cost_affected_by_count_of_satisfied_clauses(self) -> int:
        """
        Returns current state's cost: total weight is multiplied by satisfied clauses count
        """
        weight = self.sat_problem.weight(self.configuration)
        return int(weight * self.sat_problem.true_clauses_cnt(self.configuration))

    def cost_affected_by_unsatisfied_penalty_coefficient(self, unsatisfied_penalty_coefficient: int) -> int:
        """
        Returns current state's cost: the number of unsatisfied clauses multiplied by maximum weight over all literals
        and multiplied by unsatisfied_penalty_coefficient and then subtracted from the total weight
        """
        weight = self.sat_problem.weight(self.configuration)
        unsatisfied_clauses_cnt = self.sat_problem.clauses_cnt - self.sat_problem.true_clauses_cnt(self.configuration)
        return int(weight - (unsatisfied_clauses_cnt * max(self.sat_problem.weights) * unsatisfied_penalty_coefficient))

    def cost_affected_by_penalty_coefficient(self, penalty_coefficient: int) -> int:
        """
        Returns current state's cost affected by penalty coefficient
        """
        weight = self.sat_problem.weight(self.configuration)

        # F(configuration) = 1
        if self.sat_problem.is_solution(self.configuration):
            return weight * penalty_coefficient
        # F(configuration) != 1
        return int(weight * pow(self.sat_problem.true_clauses_ratio(self.configuration), penalty_coefficient))

    def better(self, other_state,
               unsatisfied_penalty_coefficient: int = None,
               penalty_coefficient: int = None
               ) -> bool:
        if unsatisfied_penalty_coefficient:
            return self.cost_affected_by_unsatisfied_penalty_coefficient(unsatisfied_penalty_coefficient) > \
                   other_state.cost_affected_by_unsatisfied_penalty_coefficient(unsatisfied_penalty_coefficient)

        if penalty_coefficient:
            return self.cost_affected_by_penalty_coefficient(penalty_coefficient) > \
                   other_state.cost_affected_by_penalty_coefficient(penalty_coefficient)

        return self.cost_affected_by_count_of_satisfied_clauses() > \
            other_state.cost_affected_by_count_of_satisfied_clauses()
