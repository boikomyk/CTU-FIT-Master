from typing import List


class Clause:
    def __init__(self):
        self.literals = []

    def is_true(self, configuration: List[bool]) -> bool:
        for literal in self.literals:
            literal_eval = configuration[literal.id - 1]
            literal_eval_with_sign = literal_eval if literal.sign > 0 else not literal_eval
            # for single clause (ex. x_1 + x_2 + x_3 ..) to be TRUE is only one TRUE enough
            if literal_eval_with_sign:
                return True
        return False

    def __str__(self):
        return ' + '.join([f"{literal}" for literal in self.literals])
