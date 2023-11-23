from models.sat_solution import SATSolution


class OutputWriter:
    @staticmethod
    def write_output(sat_solution: SATSolution):
        print('STEPS\tTIME[ms]\tSATISFIED\tWEIGHT\tCOST\tERROR\tWEIGHT_HISTORY\tTEMPERATURE_HISTORY\tCOSTS_HISTORY')
        print(
            str(sat_solution.configurations_cnt) + "\t" +
            str(round(sat_solution.time_ms, 3)) + "\t" +
            str(True if sat_solution.sat_problem.is_solution(sat_solution.solution_configuration) else False) + "\t" +
            str(sat_solution.solution_weight) + "\t" +
            str(sat_solution.costs_evolution_history[-1]) + "\t" +
            str(sat_solution.error) + "\t" +
            ",".join([str(weight) for weight in sat_solution.weights_evolution_history]) + "\t" +
            ",".join([str(temperature) for temperature in sat_solution.temperatures_evolution_history]) + "\t" +
            ",".join([str(cost) for cost in sat_solution.costs_evolution_history])
        )
