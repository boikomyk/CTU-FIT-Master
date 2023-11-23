from typing import List, Tuple

from benchmark.complexity import Complexity
from models.solution import KnapsackSolution
from helpers.logger import LOG_EVENTS

class Benchmark:
    @staticmethod
    def do_benchmark(solutions_and_complexities_lists: List[Tuple[str, List[Tuple[KnapsackSolution, Complexity]]]]):
        for set_name, solutions_and_complexities_list in solutions_and_complexities_lists:
            if LOG_EVENTS:
                print('|--------------------------|')
                print('|Benchmark for set ID : ' + set_name + (' ' if len(set_name) <= 1 else '') + ' |')
                print('|--------------------------|')
            print('STEPS\tTIME[ms]\tPRICE\tERROR\tPRICE_HISTORY\tTEMPERATURE_HISTORY')

            for solution, complexity in solutions_and_complexities_list:
                print(
                    str(complexity.configurations_cnt) + '\t'
                    + str(round(complexity.execution_time, 3)) + '\t'
                    + str(solution.solution_price) + '\t'
                    + str(solution.error) + '\t'
                    + ",".join([str(price) for price in solution.price_evolution_history]) + '\t'
                    + ",".join([str(temperature) for temperature in solution.temperatures_evolution_history])
                )
