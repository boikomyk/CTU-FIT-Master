import os.path

from models.clause import Clause
from models.literal import Literal
from models.sat_problem import SATProblem
from models.sat_reference import SATReference


class Parser:
    @staticmethod
    def load_sat_instance(path_to_input_file: str) -> SATProblem:
        if not os.path.exists(path_to_input_file):
            raise FileNotFoundError(f'File not found on path {path_to_input_file}')

        sat_problem = SATProblem()
        literals_cnt, clauses_cnt = 0, 0
        with open(os.path.join(path_to_input_file), "r") as problem_instance:
            for line in problem_instance:
                line_parts = line.strip().split(" ")

                if line_parts[0] in ['%', '0']:
                    break
                elif line_parts[0] == 'c' and len(line_parts) > 1 and line_parts[1] == 'SAT':
                    sat_problem.id = line_parts[3].split('/')[1].split('.')[0]
                elif line_parts[0] == 'p':
                    literals_cnt, clauses_cnt = int(line_parts[2].strip()), int(line_parts[3].strip())
                # weights
                elif line_parts[0] == 'w':
                    sat_problem.weights = [int(weight_str) for weight_str in line_parts[1:-1]]
                # clauses
                elif not line_parts[0].isalpha():  # not a letter
                    clause = Clause()

                    clause_parts = line_parts[:-1]
                    for literal_str in clause_parts:
                        clause.literals.append(
                            Literal(
                                id=abs(int(literal_str.strip())),
                                sign=1 if not literal_str.strip().startswith('-') else -1
                            )
                        )
                    sat_problem.clauses.append(clause)

        if sat_problem.literals_cnt != literals_cnt or sat_problem.clauses_cnt != clauses_cnt:
            raise IOError('Input file reading error.')
        return sat_problem

    @staticmethod
    def load_sat_reference(path_to_reference_file: str, problem_id: str):
        if not os.path.exists(path_to_reference_file):
            raise FileNotFoundError(f'File not found on path {path_to_reference_file}')

        with open(os.path.join(path_to_reference_file), "r") as reference_instance:
            filtered = list(filter(lambda line: line.split(' ')[0] == problem_id, reference_instance))
            if len(filtered) == 0:
                raise ValueError(f'File doesn\'t contain reference for {problem_id}')

            reference_line_parts = next(iter(filtered)).split(' ')

            return SATReference(
                id=reference_line_parts[0],
                optimal_weight=int(reference_line_parts[1]),
                optimal_configuration=[True if int(literal_evaluation) > 0 else False for literal_evaluation in reference_line_parts[2:-1]]
            )






