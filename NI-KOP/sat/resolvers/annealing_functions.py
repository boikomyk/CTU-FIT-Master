from enum import Enum

from models.sat_problem import SATProblem
from models.state import State
import numpy as np


class InitialStateGenerator(Enum):
    all_false = 1  # all literals evaluated with False
    random = 2     # random literals evaluation


class AnnealingFunctions:
    @staticmethod
    def generate_state_all_false(sat_problem: SATProblem) -> State:
        return State(
            sat_problem=sat_problem,
            configuration=[False]*sat_problem.literals_cnt
        )

    @staticmethod
    def generate_state_by_random(sat_problem: SATProblem) -> State:
        return State(
            sat_problem=sat_problem,
            configuration=np.random.choice(a=[True, False], size=sat_problem.literals_cnt).tolist()
        )
