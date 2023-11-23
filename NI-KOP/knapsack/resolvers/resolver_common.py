from enum import Enum
from timeit import default_timer as timer
from typing import List, Callable, Tuple, Dict

from helpers.logger import Logger, LOG_EVENTS
from models.solution import KnapsackSolution
from resolvers.problem_resolvers import Resolver
from benchmark.complexity import Complexity
from models.knapsack import ProblemType, Knapsack
from models.knapsackset import KnapsackSet


class ResolverType(Enum):
    bf = 1      # brute force
    bb = 2      # branch and bound
    dp_dw = 3   # dynamic programming (decomposition by weight)
    dp_dp = 4   # dynamic programming (decomposition by price)
    greedy = 5  # greedy
    redux = 6   # redux
    fptas = 7   # fptas

    def __str__(self):
        if self.name == 'bf':
            return 'Brute Force'
        elif self.name == 'bb':
            return 'Branch & Bounds'
        elif self.name == 'dp_dw':
            return 'Dynamic Programming (decomposition by weight)'
        elif self.name == 'dp_dp':
            return 'Dynamic Programming (decomposition by price)'
        elif self.name == 'greedy':
            return 'Greedy'
        elif self.name == 'redux':
            return 'Redux'
        elif self.name == 'fptas':
            return 'FPTAS'
        return self.name


resolver_to_call = {
    ResolverType.bf: Resolver.brute_force,
    ResolverType.bb: Resolver.branch_and_bound,
    ResolverType.dp_dw: Resolver.dynamic_programming_decomposition_by_weight,
    ResolverType.dp_dp: Resolver.dynamic_programming_decomposition_by_price,
    ResolverType.greedy: Resolver.greedy,
    ResolverType.redux: Resolver.redux,
    ResolverType.fptas: Resolver.fptas
}


def solve_problems_and_calculate_complexity(
        knapsack_sets_list: List[KnapsackSet],
        resolver_func: Callable[[Knapsack], Tuple],
        resolver_type: ResolverType,
        error: float
) -> List[Tuple[str, List[Tuple[KnapsackSolution, Complexity]]]]:
    if LOG_EVENTS:
        if resolver_type == ResolverType.fptas:
            Logger.log_info(f"solving problems.. selected approach is [{resolver_type}], (ERROR: {error})")
        else:
            Logger.log_info(f"solving problems.. selected approach is [{resolver_type}]")

    solutions_and_complexities_lists = list()

    for knapsack_set in knapsack_sets_list:
        solutions_and_complexities_list = list()

        for knapsack in knapsack_set.knapsack_list:
            begin = timer()
            if resolver_type == ResolverType.fptas:
                configurations_cnt, solved_instance = resolver_func(knapsack, error)
            else:
                configurations_cnt, solved_instance = resolver_func(knapsack)
            end = timer()

            # seconds * 1000000 (6x0) = microseconds
            execution_time = (end - begin) * 1000000

            # create tuple containing solved instance and it's complexity
            solution_and_complexity = (solved_instance, Complexity(
                execution_time=execution_time,
                configurations_cnt=configurations_cnt
            ))
            solutions_and_complexities_list.append(solution_and_complexity)

        solutions_and_complexities_lists.append((knapsack_set.id, solutions_and_complexities_list))

    return solutions_and_complexities_lists


def compare_solved_inst_vs_reference(solved_instance: KnapsackSolution, reference_instance_dict: Dict):
    problem_instance = solved_instance.knapsack

    # ___ CONSTRUCTIVE ___
    if problem_instance.problem_type == ProblemType.CONSTRUCTIVE:
        if solved_instance.solution_price == reference_instance_dict['price'] and\
                solved_instance.bit_combination == reference_instance_dict['solution_bit_combination']:
            return True
        else:
            return False

    # ___ DECISION ___
    elif problem_instance.problem_type == ProblemType.DECISION:
        if solved_instance.solution_price < problem_instance.min_req_price < reference_instance_dict['price']:
            return False
        else:
            return True


def compare_solution_with_reference(
        solutions_and_complexities_lists: List[Tuple[str, List[Tuple[KnapsackSolution, Complexity]]]],
        references_dict: Dict
):
    for set_name, solutions_and_complexities_list in solutions_and_complexities_lists:
        cnt_success = 0
        cnt_failed = 0
        if LOG_EVENTS: print(f" - Checking set : {set_name}")

        reference_dict = references_dict[set_name]

        for solved_instance, _ in solutions_and_complexities_list:
            reference_solved_instance = reference_dict[solved_instance.knapsack.id]
            # update error
            solved_instance.calculate_error(reference_price=int(reference_solved_instance['price']))

            if LOG_EVENTS: print(f"    - Checking inst : {solved_instance.knapsack.id}")
            if compare_solved_inst_vs_reference(
                    solved_instance=solved_instance,
                    reference_instance_dict=reference_solved_instance
            ):
                if LOG_EVENTS: print('\033[94m' + '       PASSED ✓' + '\033[0m')
                cnt_success += 1
            else:
                if LOG_EVENTS:
                    print('\033[91m' + '       FAILED ×' + '\033[0m')
                    print(f"\tSol: {''.join([str(bit) for bit in solved_instance.bit_combination])}, Price: {solved_instance.solution_price}")
                    print(f"\tRef: {''.join([str(bit) for bit in reference_solved_instance['solution_bit_combination']])}, Price: {reference_solved_instance['price']}")
                cnt_failed += 1

        if LOG_EVENTS:
            print('\033[94m' + " CNT OF PASSED TESTS : " + str(cnt_success)
                  + '/' + str(len(solutions_and_complexities_list)) + '\033[0m')
            print('\033[91m' + " CNT OF FAILED TESTS : " + str(cnt_failed)
                  + '/' + str(len(solutions_and_complexities_list)) + '\033[0m')
