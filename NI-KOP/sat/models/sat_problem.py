from typing import List


class SATProblem:
    def __init__(self):
        self.id = ''
        self.clauses = []
        self.weights = []

    @property
    def literals_cnt(self) -> int:
        return len(self.weights)

    @property
    def clauses_cnt(self) -> int:
        return len(self.clauses)

    def is_solution(self, configuration: List[bool]) -> bool:
        """
        Checks if all clauses are satisfied => F(configuration) = 1
        """
        return all([clause.is_true(configuration) for clause in self.clauses])

    def true_clauses_cnt(self, configuration: List[bool]):
        """
        Counts the number of satisfied clauses for entered configuration
        """
        return sum(1 for clause in self.clauses if clause.is_true(configuration))

    def true_clauses_ratio(self, configuration: List[bool]) -> float:
        """
        Returns the ratio of satisfied clauses to the total count
        """
        return float(self.true_clauses_cnt(configuration)) / self.clauses_cnt

    def weight(self, configuration: List[bool]) -> int:
        """
        Returns weights sum of literals set to True/1
        """
        return sum(self.weights[idx] for idx, literal_evaluation in enumerate(configuration) if literal_evaluation)

    def __str__(self):
        return f'{self.id}\n' + ''.join([f'({clause})' for clause in self.clauses])
