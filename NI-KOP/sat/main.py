import argparse

from timeit import default_timer as timer

from resolvers.annealing_functions import AnnealingFunctions, InitialStateGenerator
from resolvers.simulated_annealing import SimulatedAnnealing
from utils.helpers import is_file_path
from utils.logger import LOG_EVENTS
from utils.output_writer import OutputWriter
from utils.parser import Parser


def main():
    # Init CLI and proceed input args
    parser = init_cli()
    args = parser.parse_args()

    # load input instance
    sat_problem = Parser.load_sat_instance(args.input)
    # print(sat_problem)

    # generate initial state
    if args.state_generator == InitialStateGenerator.random:
        initial_state = AnnealingFunctions.generate_state_by_random(
            sat_problem=sat_problem
        )
    # case InitialStateGenerator.all_false
    else:
        initial_state = AnnealingFunctions.generate_state_all_false(
            sat_problem=sat_problem
        )

    begin = timer()
    # set up SimulatedAnnealing
    simulated_annealing = SimulatedAnnealing(
        sat_problem=sat_problem,
        initial_state=initial_state,
        initial_temperature=args.initial_temperature,
        cooling_coefficient=args.cooling_coefficient,
        minimal_temperature=args.minimal_temperature,
        equilibrium_coefficient=args.equilibrium_coefficient,
        penalty_coefficient=args.penalty_coefficient
    )
    if LOG_EVENTS: print(simulated_annealing)
    # execute
    solved_instance = simulated_annealing.run_sa()
    end = timer()

    # calculate result time: seconds * 1000000 (6x0) = microseconds
    execution_time = (end - begin) * 1000000
    solved_instance.time_ms = execution_time

    # Load references
    if args.reference is not None:
        solved_instance.sat_reference = Parser.load_sat_reference(
            path_to_reference_file=args.reference,
            problem_id=solved_instance.sat_problem.id
        )
        # calculate error
        solved_instance.calculate_error()
        if LOG_EVENTS: solved_instance.display_comparing_with_reference()
    if args.benchmark:
        OutputWriter.write_output(sat_solution=solved_instance)


def init_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Process input problem instances.')
    """
     0) - --input : path to the input file
     1) - --reference: path to the file containing solution/reference
     3) - --state_generator 
    """
    parser.add_argument('-in', '--input', type=is_file_path, help='paste path to input file')
    parser.add_argument('-ref', '--reference', type=is_file_path,
                        help='paste path to file containing solution/reference')
    parser.add_argument('-state_generator', '--state_generator',
                        type=lambda generator: InitialStateGenerator[generator],
                        choices=list(InitialStateGenerator), default=InitialStateGenerator.all_false)

    """
     3) - --initial_temperature 
     4) - --cooling_coefficient
     5) - --minimal_temperature
     6) - --equilibrium_coefficient
     7) - --penalty_coefficient
    """
    parser.add_argument('-initial_temperature', '--initial_temperature', type=float, help='initial temperature', default=100)
    parser.add_argument('-cooling_coefficient', '--cooling_coefficient', type=float, help='cooling coefficient', default=0.92)
    parser.add_argument('-minimal_temperature', '--minimal_temperature', type=float, help='minimal temperature', default=30)
    parser.add_argument('-equilibrium_coefficient', '--equilibrium_coefficient', type=float, help='equilibrium coefficient', default=30)
    parser.add_argument('-penalty_coefficient', '--penalty_coefficient', type=int, help='equilibrium coefficient', default=6)
    """
    8) - --benchmark
    """
    parser.add_argument('-b', '--benchmark', action='store_true', help='display benchmark')

    return parser


if __name__ == '__main__':
    main()
