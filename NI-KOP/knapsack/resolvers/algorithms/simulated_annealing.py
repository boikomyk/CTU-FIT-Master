import random
from typing import Tuple
import numpy as np
from copy import deepcopy

from models.knapsack import Knapsack
from models.solution import KnapsackSolution
from resolvers.algorithms.state import State


class SimulatedAnnealing:
    def __init__(self,
                 knapsack: Knapsack,
                 initial_state: State,
                 initial_temperature: float,
                 cooling_coefficient: float,
                 minimal_temperature: float,
                 equilibrium_coefficient: float
                 ):
        """
        :param initial_state:           initial state
        :param knapsack:                knapsack instance
        :param initial_temperature:     starting temperature
        :param cooling_coefficient:     cooling coefficient <0.8, 0.999>
        :param minimal_temperature:     temperature of frozen
        :param equilibrium_coefficient: equilibrium coefficient
        """
        self.current_temperature = initial_temperature
        self.cooling_coefficient = cooling_coefficient
        self.minimal_temperature = minimal_temperature
        self.equilibrium_coefficient = equilibrium_coefficient
        self.state = initial_state

        self.knapsack = knapsack

    def _cool(self) -> float:
        return self.current_temperature * self.cooling_coefficient

    def _frozen(self) -> bool:
        return self.current_temperature <= self.minimal_temperature

    def _equilibrium(self, iteration: int) -> bool:
        return iteration < (self.knapsack.get_items_cnt() * self.equilibrium_coefficient)

    def _try(self) -> State:
        while True:
            new_state = deepcopy(self.state)
            # get a random neighbor of the current state (differs by 1 bit -> add/remove one item)
            new_state.switch_bit_at_position(
                position=random.randint(0, self.knapsack.items_cnt - 1)
            )
            # check if state is valid
            if new_state.is_valid():
                break

        # if the new solution is better, we will accept it
        if new_state.better(self.state):
            return new_state

        # if the new solution is not better, we will still accept it if the temperature is high.
        # With this approach, we will use the worst solution in order to avoid getting stuck in local minimum.
        # But we will get a neighbor that is not that bit worse than the current state.
        delta = float(new_state.solution_price - self.state.solution_price)
        if (random.uniform(0.0, 1.0)) < np.exp(delta/self.current_temperature):
            return new_state
        return self.state

    def run_sa(self) -> Tuple[int, KnapsackSolution]:
        """
        Performs simulated annealing to find a solution
        by simulating that process of some high-temperature systems
        :return: Tuple[int, KnapsackSolution]
        """

        # prepare required vars: counter, history for price and temperatures evaluations
        configurations_cnt = 0
        price_evolution_history = [self.state.solution_price]
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
                # update price and temperature histories
                price_evolution_history.append(best_state.solution_price)
                temperatures_evolution_history.append(self.current_temperature)

            # reduce the temperature on each iteration
            self.current_temperature = self._cool()

        return configurations_cnt, KnapsackSolution(
            solution_price=best_state.solution_price,
            bit_combination=best_state.bit_combination,
            knapsack=best_state.knapsack,
            price_evolution_history=price_evolution_history,
            temperatures_evolution_history=temperatures_evolution_history
        )

    def __str__(self):
        return f"SimulatedAnnealing settings:\n" \
               f" ----------------------------------------\n"\
               f" | temperature             | { self.current_temperature} \t|\n" \
               f" | minimal_temperature     | {self.minimal_temperature} \t|\n" \
               f" | cooling_coefficient     | {self.cooling_coefficient} \t|\n" \
               f" | equilibrium_coefficient | {self.equilibrium_coefficient} \t|\n" \
               f" ----------------------------------------\n"
