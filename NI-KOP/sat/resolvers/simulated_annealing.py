import random
import numpy as np
from copy import deepcopy

from models.sat_problem import SATProblem
from models.sat_solution import SATSolution
from models.state import State


class SimulatedAnnealing:
    def __init__(self,
                 sat_problem: SATProblem,
                 initial_state: State,
                 initial_temperature: float,
                 cooling_coefficient: float,
                 minimal_temperature: float,
                 equilibrium_coefficient: float,
                 penalty_coefficient: int
                 ):
        """
        :param initial_state:           initial state
        :param initial_temperature:     starting temperature
        :param cooling_coefficient:     cooling coefficient <0.8, 0.999>
        :param minimal_temperature:     temperature of frozen
        :param equilibrium_coefficient: equilibrium coefficient
        :param penalty_coefficient:     penalty coefficient

        """
        self.sat_problem = sat_problem
        self.state = initial_state

        self.current_temperature = initial_temperature
        self.cooling_coefficient = cooling_coefficient
        self.minimal_temperature = minimal_temperature
        self.equilibrium_coefficient = equilibrium_coefficient
        self.penalty_coefficient = penalty_coefficient

    def _cool(self) -> float:
        return self.current_temperature * self.cooling_coefficient

    def _frozen(self) -> bool:
        return self.current_temperature <= self.minimal_temperature

    def _equilibrium(self, iteration: int) -> bool:
        return iteration < (self.sat_problem.literals_cnt * self.equilibrium_coefficient)

    def _try(self) -> State:
        new_state = deepcopy(self.state)
        # get a random neighbor of the current state (differs by 1 bit -> change literal evaluation)
        new_state.switch_literal_evaluation_at_position(
            position=random.randint(0, self.sat_problem.literals_cnt - 1)
        )

        # if the new solution is better, we will accept it
        if new_state.better(
                other_state=self.state,
                penalty_coefficient=self.penalty_coefficient
        ):
            return new_state

        # if the new solution is not better, we will still accept it if the temperature is high.
        # With this approach, we will use the worst solution in order to avoid getting stuck in local minimum.
        # But we will get a neighbor that is not that bit worse than the current state.
        delta = float(new_state.cost_affected_by_penalty_coefficient(self.penalty_coefficient) -
                      self.state.cost_affected_by_penalty_coefficient(self.penalty_coefficient))
        if (random.uniform(0.0, 1.0)) < np.exp(delta/self.current_temperature):
            return new_state
        return self.state

    def run_sa(self) -> SATSolution:
        """
        Performs simulated annealing to find a solution
        by simulating that process of some high-temperature systems
        """

        # prepare required vars: counter, history for price and temperatures evaluations
        configurations_cnt = 0
        weights_evolution_history = [self.state.sat_problem.weight(self.state.configuration)]
        costs_evolution_history = [self.state.cost_affected_by_penalty_coefficient(self.penalty_coefficient)]
        temperatures_evolution_history = [self.current_temperature]

        best_state = deepcopy(self.state)

        # repeat this process until the current temperature is less than the final temperature
        while not self._frozen():
            iteration = 0
            # stay on this temperature for a while (equilibrium)
            while self._equilibrium(iteration):
                # get a random neighbor of the current state
                self.state = self._try()

                if self.state.better(best_state) and self.state.is_valid():
                    # update best state
                    best_state = deepcopy(self.state)

                # increment counters
                iteration += 1
                configurations_cnt += 1
                # update weights and temperature histories
                weights_evolution_history.append(best_state.sat_problem.weight(best_state.configuration))
                temperatures_evolution_history.append(self.current_temperature)
                costs_evolution_history.append(best_state.cost_affected_by_penalty_coefficient(self.penalty_coefficient))

            # reduce the temperature on each iteration
            self.current_temperature = self._cool()

        return SATSolution(
            sat_problem=best_state.sat_problem,
            solution_configuration=best_state.configuration,
            solution_weight=best_state.sat_problem.weight(best_state.configuration),
            configurations_cnt=configurations_cnt,
            weights_evolution_history=weights_evolution_history,
            temperatures_evolution_history=temperatures_evolution_history,
            costs_evolution_history=costs_evolution_history
        )

    def __str__(self):
        return f"SimulatedAnnealing settings:\n" \
               f" ----------------------------------------\n"\
               f" | temperature             | { self.current_temperature} \t|\n" \
               f" | minimal_temperature     | {self.minimal_temperature} \t|\n" \
               f" | cooling_coefficient     | {self.cooling_coefficient} \t|\n" \
               f" | equilibrium_coefficient | {self.equilibrium_coefficient} \t|\n" \
               f" | penalty_coefficient     | {self.penalty_coefficient}  \t|\n" \
               f" ----------------------------------------\n"
