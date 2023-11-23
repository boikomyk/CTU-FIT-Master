from models.knapsack import Knapsack


class KnapsackSolution:
    def __init__(self, solution_price: int, bit_combination: list, knapsack: Knapsack,
                 price_evolution_history: list=[],
                 temperatures_evolution_history: list=[]
                 ):
        self.solution_price = solution_price
        self.bit_combination = bit_combination
        self.knapsack = knapsack
        self.error = 0.0
        # for SimulatedAnnealing
        self.price_evolution_history = price_evolution_history
        self.temperatures_evolution_history = temperatures_evolution_history

    def calculate_solution_weight(self) -> int:
        return sum(self.knapsack.items_list[item_index].weight for item_index, bit in enumerate(self.bit_combination) if bit == 1)

    def calculate_error(self, reference_price: int):
        # at least one of prices should be different from zero
        if self.solution_price != 0 or reference_price != 0:
            # |solution_price - reference_price| / |max(solution_price, reference_price)|
            self.error = abs(self.solution_price - reference_price) / abs(max(self.solution_price, reference_price))
