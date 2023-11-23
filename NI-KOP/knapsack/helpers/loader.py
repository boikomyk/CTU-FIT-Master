import os
import re

from models.item import Item
from models.knapsack import Knapsack, ProblemType
from models.knapsackset import KnapsackSet
from typing import List, Optional, Dict
from helpers.logger import Logger, LOG_EVENTS


class Loader:
    @staticmethod
    def parse_items(items_str_list: list) -> List[Item]:
        items_list = list()
        for weight, price in zip(items_str_list[0::2], items_str_list[1::2]):
            items_list.append(
                Item(
                    weight=int(weight),
                    price=int(price)
                )
            )
        return items_list

    @staticmethod
    def parse_knapsack(line_str: str) -> Knapsack:
        # Detect problem type
        if line_str.startswith('-'):
            # ___ DECISION ___
            problem_instances_list = line_str.split(' ', 4)

            # Decision problem contains additional attr: min_req_price
            knapsack_obj = Knapsack(
                id=int(problem_instances_list[0][1:]),
                items_cnt=int(problem_instances_list[1]),
                capacity=int(problem_instances_list[2]),
                min_req_price=int(problem_instances_list[3]),
                problem_type=ProblemType.DECISION
            )
            # weights & prices
            items_str_list = problem_instances_list[4].split(' ')
        else:
            # ___ CONSTRUCTIVE ___
            problem_instances_list = line_str.split(' ', 3)
            #
            knapsack_obj = Knapsack(
                id=int(problem_instances_list[0]),
                items_cnt=int(problem_instances_list[1]),
                capacity=int(problem_instances_list[2]),
                min_req_price=0,
                problem_type=ProblemType.CONSTRUCTIVE
            )
            # weights & prices
            items_str_list = problem_instances_list[3].split(' ')

        knapsack_obj.items_list.extend(Loader.parse_items(items_str_list))
        return knapsack_obj

    @staticmethod
    def load_dataset(path_to_dir: str, filename: str) -> KnapsackSet:
        id_pos = re.search('\d', filename)
        set_id = filename.split('_')[0][id_pos.start():]
        knapsack_set = KnapsackSet(id=set_id)

        if LOG_EVENTS: print(f"  - loading set : {filename} [ID: {knapsack_set.id}]")
        with open(os.path.join(path_to_dir, filename), "r") as dataset:
            for line in dataset:
                knapsack_set.knapsack_list.append(Loader.parse_knapsack(line))
        return knapsack_set

    @staticmethod
    def load_input_data(path: str, max_cnt_to_read: int) -> List[KnapsackSet]:
        if LOG_EVENTS: Logger.log_info("loading problem\'s instances")
        knapsack_sets = list()

        # validate if path exists
        if os.path.exists(path):
            # check if it's a dir or file
            if os.path.isdir(path):
                # read only files matching `_inst`
                datasets_files = sorted([filename for filename in os.listdir(path) if '_inst' in filename],
                                        key=lambda name: int(name[:name.rfind("_")][2:]))

                for _, dataset_file in zip(range(max_cnt_to_read), datasets_files):
                    knapsack_sets.append(Loader.load_dataset(path, dataset_file))

            elif os.path.isfile(path):
                knapsack_sets.append(Loader.load_dataset(os.path.dirname(path), os.path.basename(path)))
        return knapsack_sets


    @staticmethod
    def read_references(path_to_ref: str, proceeded_dataset_names: list) -> Optional[Dict]:
        references_dict = None

        if os.path.exists(path_to_ref) and os.path.isdir(path_to_ref):
            # filter for references files by string pattern `_sol`
            reference_files = sorted([filename for filename in os.listdir(path_to_ref) if '_sol' in filename])
            references_dict = {}

            # read reference for proceeded datasets
            for proceeded_dataset_name in proceeded_dataset_names:
                # find according solution file
                r = re.compile('^[A-Z]{2,}' + proceeded_dataset_name + '_sol.dat')
                reference_file_name = list(filter(r.search, reference_files))[0]

                if LOG_EVENTS: print(f"  - loading ref : {reference_file_name}, [ID: {proceeded_dataset_name}]")

                references_dict[proceeded_dataset_name] = {}
                with open(os.path.join(path_to_ref, reference_file_name), "r") as reference_file_content:
                    # line format: ID, n, sol_price, 0/1, ...
                    for line in reference_file_content:
                        solution_instance_list = line.split(' ', 3)

                        # parse parameters from line
                        id = int(solution_instance_list[0])
                        n = int(solution_instance_list[1])
                        sol_price = int(solution_instance_list[2])
                        str_set_items_bits = solution_instance_list[3].rstrip('\r\n')

                        bit_combination_int_representation = [0]*n
                        for index, digit in enumerate(str_set_items_bits.split()):
                            bit_combination_int_representation[index] = int(digit)

                        # save to dict
                        references_dict[proceeded_dataset_name][id] = {'n': n, 'price': sol_price, 'solution_bit_combination': bit_combination_int_representation}
        return references_dict
