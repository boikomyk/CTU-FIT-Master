#coding: utf-8

import argparse

# import helpers
from helpers.loader import Loader
from helpers.logger import Logger, LOG_EVENTS

# import resolvers
from helpers.output_writter import OutputWritter
from helpers.utils import is_dir_or_file_path
from resolvers.resolver_common import ResolverType, resolver_to_call
from resolvers.resolver_common import solve_problems_and_calculate_complexity, compare_solution_with_reference

from benchmark.benchmark import Benchmark

def main():
    # Init CLI and proceed input args
    parser = init_cli()
    args = parser.parse_args()

    # Load input files and wrap them into objects
    knapsack_sets_list = Loader.load_input_data(
        path=args.input,
        max_cnt_to_read=args.count
    )

    # Choose solver
    resolver_func = resolver_to_call[args.resolver]

    # Solve
    solutions_and_complexities_lists = solve_problems_and_calculate_complexity(
        knapsack_sets_list=knapsack_sets_list,
        resolver_func=resolver_func,
        resolver_type=args.resolver,
        error=args.error
    )

    # Load references
    if args.reference is not None:
        proceed_dataset_names = [i[0] for i in solutions_and_complexities_lists]
        if LOG_EVENTS: Logger.log_info('reading references')
        references_dict = Loader.read_references(
            path_to_ref=args.reference,
            proceeded_dataset_names=proceed_dataset_names
        )

        # Compare with references
        if references_dict is not None:
            if LOG_EVENTS: Logger.log_info('comparing with references')
            compare_solution_with_reference(
                solutions_and_complexities_lists=solutions_and_complexities_lists,
                references_dict=references_dict
            )
        else:
            if LOG_EVENTS: Logger.log_warning('According references were not found')
    else:
        if LOG_EVENTS: Logger.log_warning('Path with references isn\'t set')

    # Start benchmark
    if args.benchmark:
        Benchmark.do_benchmark(solutions_and_complexities_lists)

    # Write solution:
    if args.output:
        OutputWritter.write_output(solutions_and_complexities_lists)


def init_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Process input problem instances.')
    """
     0) - resolver type bf/bb/dp_dw/dp_dp/greedy/redux/fptas
     1) - --count : count of files to proceed
     2) - --input : path to the dir with testing files
     3) - --reference: path to the dir with references
     4) - --benchmark: turn on/off benchmark
    """
    parser.add_argument('resolver', type=lambda resolver: ResolverType[resolver], choices=list(ResolverType), default=ResolverType.bf)
    parser.add_argument('-cnt', '--count', type=int, default=24)
    parser.add_argument('-in', '--input', type=is_dir_or_file_path, help='paste path to input files')
    parser.add_argument('-ref', '--reference', type=is_dir_or_file_path, help='paste path with references')
    parser.add_argument('-err', '--error', type=float, help='relative error', default=0.01)
    parser.add_argument('-b', '--benchmark', action='store_true', help='turn on/off benchmark')
    parser.add_argument('-o', '--output', action='store_true', help='write solution to output')
    return parser


if __name__ == '__main__':
    main()
