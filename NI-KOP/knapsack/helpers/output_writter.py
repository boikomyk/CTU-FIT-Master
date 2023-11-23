from typing import List, Tuple

from benchmark.complexity import Complexity
from models.solution import KnapsackSolution


class OutputWritter:
    @staticmethod
    def write_output(solutions_and_complexities_lists: List[Tuple[str, List[Tuple[KnapsackSolution, Complexity]]]]):
        for set_name, solutions_and_complexities_list in solutions_and_complexities_lists:
            for index, (solution, complexity) in enumerate(solutions_and_complexities_list, 1):
                bit_combination_str = " ".join(map(lambda bit: str(bit), solution.bit_combination))
                print(f"{index} {solution.knapsack.items_cnt} {solution.solution_price} {bit_combination_str}")
