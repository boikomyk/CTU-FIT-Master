import sys
from typing import Tuple, List

from models.knapsack import Knapsack, ProblemType
from models.solution import KnapsackSolution
from copy import deepcopy

from collections import deque


# __________________________________________ HELP CLASSES SCOPE __________________________________________
class Node:
    def __init__(self, level: int = 0, selected_items_indexes: list = [],
                 total_price: int = 0, total_weight: int = 0, bound: int = 0):
        """
        level: level of node in decision tree
        total_price: profit of nodes on path from root to this node (including this node)
        bound: upper bound of maximum profit in subtree of this node
        """
        self.level = level
        self.selected_items_indexes = selected_items_indexes
        self.total_price = total_price
        self.total_weight = total_weight
        self.bound = bound


class Resolver:
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # __________________________________________ BRUTE_FORCE ______________________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    @staticmethod
    def brute_force(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        # help functions scope
        is_valid_item = lambda current_bits_combination, item_bit_index:\
            (current_bits_combination & (1 << item_bit_index)) != 0

        # All possible combination of items in knapsack
        combinations_cnt = 1 << knapsack.get_items_cnt()

        best_combination = 0
        best_price = 0
        best_weight = 0

        # we should iterate through all possible combinations
        configurations_cnt = combinations_cnt
        # iterate through all possible combinations
        for current_bits_comb in range(0, combinations_cnt):
            temp_weight = 0
            temp_price = 0

            # iterate through all knapsack items
            for item_bit_index in range(knapsack.get_items_cnt()):

                # check if item is valid for current bit combination
                if is_valid_item(current_bits_comb, item_bit_index):
                    temp_weight += knapsack.items_list[item_bit_index].weight
                    temp_price += knapsack.items_list[item_bit_index].price

            # if fulfilled problem conditions: max_capacity & required min price
            if knapsack.is_valid_knapsack(
                    weight=temp_weight,
                    price=temp_price
            ):
                # compare with previous best combination
                if temp_price > best_price or (temp_price == best_price and temp_weight < best_weight):
                    best_combination = current_bits_comb
                    best_weight = temp_weight
                    best_price = temp_price

                if knapsack.problem_type == ProblemType.DECISION:
                    configurations_cnt = current_bits_comb + 1
                    # stop iteration process, we've already found solution
                    break

        list_of_set_items_bits = [0]*knapsack.get_items_cnt()
        index_of_set_bit = 0
        while best_combination:
            if (best_combination & 0x1) == 1:
                list_of_set_items_bits[index_of_set_bit] = 1

            best_combination >>= 1
            index_of_set_bit += 1

        return configurations_cnt, KnapsackSolution(
            solution_price=best_price,
            bit_combination=list_of_set_items_bits,
            knapsack=knapsack
        )

    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # __________________________________________ BRANCH_AND_BOUNDS ________________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    @staticmethod
    def branch_and_bound(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        # make an empty queue (for traversing the node)
        candidate_queue = deque()

        # create items list of ratio: price per weight
        price_per_weight_list = list()
        for index, item in enumerate(knapsack.items_list):
            # price/weight
            price_per_weight_list.append((index, item.price/float(item.weight)))
        # sort it in descending order
        price_per_weight_list = sorted(price_per_weight_list, key=lambda x: x[1], reverse=True)

        # initialize best solution
        best_solution = Node()

        start_node_bound = Resolver.get_bound_price(
            node=best_solution,
            items_cnt=knapsack.get_items_cnt(),
            capacity=knapsack.capacity,
            items=knapsack.items_list,
            price_per_weight_list=price_per_weight_list
        )
        # dummy node at starting (total price and weight of start node are 0)
        start_node = Node(bound=start_node_bound)
        candidate_queue.appendleft(start_node)

        # configurations_cnt(or iterations cnt)
        configurations_cnt = 0

        while len(candidate_queue) > 0:
            # check if satisfied solution with best profit was already found (only for DECISION type problems)
            if (knapsack.problem_type == ProblemType.DECISION) and\
                    knapsack.is_valid_knapsack(best_solution.total_weight, best_solution.total_price):
                break

            # dequeue a node and update steps cnt
            current_node = candidate_queue.pop()
            configurations_cnt += 1

            # if the current node bound value is greater than current total price, then go to processing steps
            if current_node.bound > best_solution.total_price:
                # resolve next item index and then obtain it's price and weight
                next_item_index = price_per_weight_list[current_node.level][0]
                next_item_price = knapsack.items_list[next_item_index].price
                next_item_weight = knapsack.items_list[next_item_index].weight

                # make the left child node (YES case, to add)
                # increment level and update total price and weight
                node_to_add = Node(
                    level=current_node.level + 1,
                    selected_items_indexes=current_node.selected_items_indexes + [next_item_index],
                    total_price=current_node.total_price + next_item_price,
                    total_weight=current_node.total_weight + next_item_weight,
                    bound=current_node.bound
                )

                # if the total weight is less or equal to capacity and price condition is satisfied
                # then update the current best solution
                if node_to_add.total_weight <= knapsack.capacity:
                    if (node_to_add.total_price > best_solution.total_price) or\
                            (node_to_add.total_price == best_solution.total_price and node_to_add.total_weight < best_solution.total_weight):
                        best_solution = node_to_add

                    # If bound value is greater than total price, then only push into queue
                    if node_to_add.bound > best_solution.total_price:
                        candidate_queue.appendleft(node_to_add)

                # make out right child node (NO case, not to add)
                # do the same thing,  but without taking the item in knapsack, so only increment level
                node_not_to_add = Node(
                    level=current_node.level + 1,
                    selected_items_indexes=current_node.selected_items_indexes,
                    total_price=current_node.total_price,
                    total_weight=current_node.total_weight,
                    bound=current_node.bound
                )
                # get the upper bound to decide whether to add note to queue or not
                node_not_to_add.bound = Resolver.get_bound_price(
                    node=node_not_to_add,
                    items_cnt=knapsack.get_items_cnt(),
                    capacity=knapsack.capacity,
                    items=knapsack.items_list,
                    price_per_weight_list=price_per_weight_list
                )

                if node_not_to_add.bound > best_solution.total_price:
                    candidate_queue.appendleft(node_not_to_add)

        best_combination = [0] * knapsack.get_items_cnt()
        if not knapsack.is_valid_knapsack(best_solution.total_weight, best_solution.total_price):
            return configurations_cnt, KnapsackSolution(0, best_combination, knapsack)

        # fill the array of set items with solution
        for selected_item_index in best_solution.selected_items_indexes:
            best_combination[selected_item_index] = 1

        return configurations_cnt, KnapsackSolution(best_solution.total_price, best_combination, knapsack)

    # help function for calculating bound of Node for "branchAndBound" resolver
    @staticmethod
    def get_bound_price(node: Node, items_cnt: int, capacity: int, items,
                        price_per_weight_list: List[Tuple[int, float]]) -> int:
        """
        returns bound of profit in subtree rooted with Node
        """

        # if weight overcomes the knapsack capacity, return 0
        if node.total_weight >= capacity:
            return 0

        # init bound on profit by current total price
        upper_bound = node.total_price
        current_proceeding_level = node.level
        total_weight = node.total_weight

        while True:
            # check if current proceeded level isn't greater then items cnt limit
            if current_proceeding_level >= items_cnt:
                break

            current_item_index = price_per_weight_list[current_proceeding_level][0]
            current_item = items[current_item_index]

            # if total weight plus current item weight greater then capacity, then:
            if total_weight + current_item.weight > capacity:
                # include item partially for upper bound on profit
                upper_bound += (capacity - total_weight) * (current_item.price / current_item.weight)
                break
            # ..lower or equal:
            else:
                upper_bound += current_item.price
                total_weight += current_item.weight
                current_proceeding_level += 1
        return upper_bound

    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # ________________________________________ DYNAMIC PROGRAMMING  _______________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________

    # ______________________________________ 1.decomposition by weight ____________________________________
    @staticmethod
    def dynamic_programming_decomposition_by_weight(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        # prepare required vars
        # compute count of rows and columns:
        # - rows:    items total count
        # - columns: knapsack's capacity
        capacity_columns_cnt = knapsack.capacity
        items_indexes_rows_cnt = len(knapsack.items_list)

        # create help memory table of according sizes
        memory_table = [
            # init table with zero values
            [0 for _ in range(capacity_columns_cnt + 1)] for _ in range(items_indexes_rows_cnt + 1)
        ]

        configurations_cnt = 0
        # Build help memory table in bottom up manner
        for item_index in range(items_indexes_rows_cnt + 1):
            for capacity_index in range(capacity_columns_cnt + 1):
                configurations_cnt += 1

                # check basic/trivial conditions:
                # - zero items or
                # - zero knapsack capacity
                if item_index == 0 or capacity_index <= 0:
                    memory_table[item_index][capacity_index] = 0
                    continue

                # get current proceeding item
                current_item = knapsack.items_list[item_index - 1]
                #  if weight of current item is lower or equal to the remaining knapsack's capacity then
                if current_item.weight <= capacity_index:
                    # return the maximum of two cases:
                    # - current item included or
                    # - not included
                    memory_table[item_index][capacity_index] = max(
                        current_item.price + memory_table[item_index - 1][capacity_index - current_item.weight],
                        memory_table[item_index - 1][capacity_index]
                    )
                # otherwise current proceeding item cannot be included
                else:
                    memory_table[item_index][capacity_index] = memory_table[item_index - 1][capacity_index]

        # resolve best price and prepare bit container for storing best bit combination
        best_price = memory_table[items_indexes_rows_cnt][capacity_columns_cnt]
        best_combination = [0] * knapsack.get_items_cnt()

        # resolve indexes
        current_item_index = items_indexes_rows_cnt
        current_weight_index = memory_table[current_item_index].index(max(memory_table[current_item_index]))

        weight_in_knapsack = 0
        # reconstruct the traveled path
        while True:
            if current_item_index <= 0 or current_weight_index > knapsack.capacity - weight_in_knapsack:
                break
            # get current proceeding item
            current_item = knapsack.items_list[current_item_index - 1]
            # check if item at this position was added: easy comparing actual cell's value with cell's value above
            if memory_table[current_item_index][current_weight_index] != memory_table[current_item_index - 1][current_weight_index]:
                best_combination[current_item_index - 1] = 1
                # calculate remaining capacity
                current_weight_index -= current_item.weight
                weight_in_knapsack += current_item.weight
            current_item_index -= 1

        return configurations_cnt, KnapsackSolution(best_price, best_combination, knapsack)

    # ______________________________________ 2.decomposition by price _____________________________________
    @staticmethod
    def dynamic_programming_decomposition_by_price(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        # prepare required vars
        infinity = sys.maxsize
        # compute count of rows and columns:
        # - rows:    total sum of all items
        # - columns: items total count
        items_total_sum = sum(item.price for item in knapsack.items_list)
        items_total_count = len(knapsack.items_list)
        # create help memory table of according sizes, where each cell represents summary weight of  first i items
        memory_table = [
            # init table with zero values
            [0 for _ in range(items_total_count + 1)] for _ in range(items_total_sum + 1)
        ]

        # provide table initialisation
        # W(0, 0) = 0
        # W(c, 0) = infinity for any c > 0

        # zero items count case(first column): set infinity value for all knapsack prices (excluding first table's cell)
        for knapsack_current_price in range(1, items_total_sum + 1):
            memory_table[knapsack_current_price][0] = infinity
        # also init first raw for items that price are equal ot 1 (set infinity for others)
        for item_index in range(items_total_count + 1):
            memory_table[1][item_index] = knapsack.items_list[item_index - 1].weight \
                if 1 == knapsack.items_list[item_index - 1].price else infinity

        # init steps counter
        configurations_cnt = 0
        # iterate through the memory table
        for knapsack_current_price in range(2, items_total_sum + 1):
            for item_index in range(1, items_total_count + 1):
                # get current proceeding item and update steps cnt
                current_item = knapsack.items_list[item_index - 1]
                configurations_cnt += 1

                # previous reached weight should be stored in previous column W(c, i - 1)
                previous_weight = memory_table[knapsack_current_price][item_index - 1]

                index = knapsack_current_price - current_item.price

                if index < 0:
                    # if index is negative, the weight remains the same
                    memory_table[knapsack_current_price][item_index] = previous_weight
                else:
                    # otherwise
                    # resolve weight to add (zero or weight of current proceeding item)
                    weight_to_add = current_item.weight if memory_table[index][item_index - 1] != infinity else 0
                    # W(c, i) = min(W(c, i - 1), W(c, i - 1 ) + w_c) for any c > 0
                    memory_table[knapsack_current_price][item_index] = min(previous_weight, memory_table[index][item_index - 1] + weight_to_add)

        # prepare vars for storing solution's params after path reconstruction process
        best_price = 0
        best_combination = [0] * knapsack.get_items_cnt()

        # iterate from the end ~ reverse order
        for knapsack_current_price in range(items_total_sum, -1, -1):
            # The solution is max(W(c, n)) <= capacity
            if memory_table[knapsack_current_price][items_total_count] <= knapsack.capacity:
                best_price = knapsack_current_price
                break

        # set indexes
        solution_price_index = best_price
        items_index = items_total_count
        # reconstruct the traveled path
        while solution_price_index > 0:
            if items_index <= 0:
                break

            # check if at this position was added item: easy comparing actual cell's value with cell's value above
            if memory_table[solution_price_index][items_index] != memory_table[solution_price_index][items_index - 1]:
                solution_price_index -= knapsack.items_list[items_index - 1].price
                best_combination[items_index - 1] = 1
            items_index -= 1

        return configurations_cnt, KnapsackSolution(best_price, best_combination, knapsack)

    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # ______________________________________________ GREEDY _______________________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    @staticmethod
    def greedy(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        # create items list of ratio: price per weight
        price_per_weight_list = list()
        for index, item in enumerate(knapsack.items_list):
            # price/weight
            price_per_weight_list.append((index, item.price/float(item.weight)))
        # sort it in descending order
        price_per_weight_list = sorted(price_per_weight_list, key=lambda x: x[1], reverse=True)
        sorted_items_indexes = [price_per_weight[0] for price_per_weight in price_per_weight_list]

        # prepare required vars
        configurations_cnt = 0
        temporary_weight = 0
        temporary_price = 0
        best_combination = [0] * knapsack.get_items_cnt()
        # iterate through sorted `price per weight` items indexes
        for item_index in sorted_items_indexes:
            # add items sequentially until the knapsack is full
            # in each step insert to knapsack item with best ratio value (in case of enough remaining knapsack capacity)

            # update counter
            configurations_cnt += 1

            # get current proceeding item
            current_item = knapsack.items_list[item_index]
            # check if current item can be included in knapsack
            if temporary_weight + current_item.weight > knapsack.capacity:
                continue

            # update temporary weight, price a bit combination
            temporary_weight += current_item.weight
            temporary_price += current_item.price
            best_combination[item_index] = 1

            if knapsack.problem_type == ProblemType.DECISION and knapsack.is_valid_knapsack(temporary_weight, temporary_price):
                break

        return configurations_cnt, KnapsackSolution(temporary_price, best_combination, knapsack)

    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # _______________________________________________ REDUX _______________________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    @staticmethod
    def redux(knapsack: Knapsack) -> Tuple[int, KnapsackSolution]:
        """
        Modification of GREEDY heuristic, which also considers solution with the single most expensive item
        """
        # 1. solve instance with a GREEDY approach
        greedy_configurations_cnt, greedy_knapsack_solution = Resolver.greedy(
            knapsack=knapsack
        )

        # 2. solve the same instance with a REDUX modification
        # set for a while GREEDY as the final solution
        final_solution = greedy_knapsack_solution

        # sort item by price in descending order
        items_indexes_with_price_list = list()
        for index, item in enumerate(knapsack.items_list):
            items_indexes_with_price_list.append((index, item.price))
        items_indexes_with_price_list = sorted(items_indexes_with_price_list, key=lambda x: x[1], reverse=True)
        sorted_items_indexes = [item_index_with_price[0] for item_index_with_price in items_indexes_with_price_list]

        # prepare required vars
        redux_configurations_cnt = 0
        redux_temporary_weight = 0
        redux_temporary_price = 0
        redux_best_combination = [0] * knapsack.get_items_cnt()
        # iterate through sorted by price items indexes
        for item_index in sorted_items_indexes:
            # update redux steps counter
            redux_configurations_cnt += 1

            # get current proceeding item
            current_item = knapsack.items_list[item_index]
            # check if current item can be included in knapsack
            if redux_temporary_weight + current_item.weight > knapsack.capacity:
                continue

            # update temporary weight, price a bit combination
            redux_temporary_weight += current_item.weight
            redux_temporary_price += current_item.price
            redux_best_combination[item_index] = 1

            # 3. compare GREEDY solution with REDUX modification and choose the best one
            if knapsack.is_valid_knapsack(redux_temporary_weight, redux_temporary_price) and (
                    # redux solution price is greater than greedy or price is equal but total weight is lower
                    redux_temporary_price > greedy_knapsack_solution.solution_price or
                    (
                        redux_temporary_price == greedy_knapsack_solution.solution_price and
                        redux_temporary_weight < greedy_knapsack_solution.calculate_solution_weight()
                    )
            ):
                # change solution with REDUX and stop iteration
                final_solution = KnapsackSolution(redux_temporary_price, redux_best_combination, knapsack)
                break

        # recalculate total configurations_cnt
        total_configurations_cnt = greedy_configurations_cnt + redux_configurations_cnt
        return total_configurations_cnt, final_solution

    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    # _______________________________________________ FPTAS _______________________________________________
    # _____________________________________________________________________________________________________
    # _____________________________________________________________________________________________________
    @staticmethod
    def fptas(knapsack: Knapsack, error: float = 0.1) -> Tuple[int, KnapsackSolution]:
        """
        Lets introduce a maximum relative error and decrease the sum of prices =>
         decrease an overall space that memory table from dynamic programming with decomposition by price requires
        """
        # create deep copy of knapsack
        knapsack_modified = deepcopy(knapsack)
        # resolve knapsack item with greatest price
        max_price = max(item.price for item in knapsack_modified.items_list)
        # calculate the denominator: K = (eps * C_M) / items_cnt
        K = (error * max_price) / len(knapsack_modified.items_list)
        # than build a modified items version: decrease prices
        for modified_item in knapsack_modified.items_list:
            modified_item.price = int(modified_item.price / K)

        # than modify knapsack object
        knapsack_modified.min_req_price = int(knapsack_modified.min_req_price / K)

        # solve modified knapsack instance with dynamic programming with decomposition by price
        configurations_cnt, solution = Resolver.dynamic_programming_decomposition_by_price(
            knapsack=knapsack_modified
        )
        # recalculate solution price
        solution_price = sum(knapsack.items_list[item_index].price for item_index, bit in enumerate(solution.bit_combination) if bit == 1)
        return configurations_cnt, KnapsackSolution(solution_price, solution.bit_combination, knapsack)
