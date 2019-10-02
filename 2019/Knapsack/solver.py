"""
The solver manager for the Coursera Dynamic Optimization Knapsack homework.
"""

from collections import namedtuple
from time import process_time
from typing import List, Tuple

from dynamic_prog import dynamic_prog
from bb_solver import bb_solver


Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])


def apply_solver(solver, greedy_value, items_count, capacity, sorted_items,
                 verbose_outline, verbose_tracking) -> Tuple[int, int, List[int]]:
    """

    :param solver: the solver to be used
    :param greedy_value: the value produced by the greedy-by-density search
    :param items_count: the number of items in the items list
    :param capacity: the capacity of the knapsack
    :param sorted_items: the items from which to select, sorted by density
    :param verbose_outline: whether a verbose outline should be printed
    :param verbose_tracking: whether more detailed information should be printed
    :return:
    """
    if verbose_outline:
        print(f'\n{solver.__name__}\n{"".join(["-"]*len(solver.__name__))}')

    start = process_time()
    (value, taken_items_sorted_by_density) = solver(greedy_value, items_count, capacity, sorted_items, verbose_tracking)
    elapsed_time = round(process_time() - start, 2)

    # Convert the taken items from using the sorted_items indices to using the original indices.
    # Then sort those indices.
    taken_items = sorted([sorted_items[dpbb_index].index for dpbb_index in taken_items_sorted_by_density])
    # All results are optimal except greedy_by_density
    is_optimal = int(solver is not greedy_by_order)
    if verbose_outline:
        print(f' -> Elapsed time: {elapsed_time} sec')
        output_data = f'{value} {is_optimal}\n{taken_items}'
        print(output_data)

    return (value, is_optimal, taken_items)


def greedy_by_order(_items_count, capacity, items, _verbose_tracking) -> Tuple[int, List[int]]:
    """

    :param _items_count: not used
    :param capacity: the capacity of the knapsack
    :param items: the items from which to select
    :param _verbose_tracking: not used
    :return:
    """
    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    weight = 0
    taken_greedy = []
    for (index, item) in enumerate(items):
        if weight + item.weight <= capacity:
            taken_greedy.append(index)
            value += item.value
            weight += item.weight
    return (value, sorted(taken_greedy))


def make_an_Item(index: int, value: int, weight: int):
    """

    :param index:
    :param value:
    :param weight:
    :return:
    """
    return Item(index=index, value=value, weight=weight, density=value/weight)


def solve_a_dataset(input_data, solvers, prob_nbr, verbose_outline, verbose_tracking) -> str:
    """
    Run the indicated solvers on the input_data dataset.
    Select the best result.
    :param input_data: The input file as a single string
    :param solvers: The solvers to use
    :param prob_nbr: the problem number
    :param verbose_outline: whether a verbose outline should be printed
    :param verbose_tracking: whether more detailed information should be printed
    :return: a string formatted for the Coursera grader.
    """
    equals_line = "==" * 65
    lines = input_data.split('\n')
    (items_count, capacity) = map(int, lines[0].split())
    problem_size = round(items_count * capacity / 1E6)  # 1E6 == 1,000,000 == 1 million
    # Each result is (value, opt, taken)
    items = [make_an_Item(i, *map(int, lines[i + 1].split())) for i in range(items_count)]
    sorted_items: List[Item] = sorted(items, key=lambda item: item.density, reverse=True)
    greedy_value = greedy_by_order(items_count, capacity, sorted_items, verbose_tracking)[0]
    print(f'\n{equals_line}\n{prob_nbr})'
                                      f' {file_location}. '
                                      f'Problem size (items_count ({items_count}) * capacity ({capacity})):'
                                      f' {problem_size} million; '
                                      f'greedy_by_density: {greedy_value}\n'
                                      f'{equals_line}')
    if tracking_verbosity:
        print('\nItems')
        for (n, item) in enumerate(items):
            print(f'{n}. {item}')
        print('\nDensity-sorted items')
        for (n, item) in enumerate(sorted_items):
            print(f'{n}. {item}')

    results = [apply_solver(solver, greedy_value, items_count, capacity, sorted_items,
                            verbose_outline, verbose_tracking)
               for solver in solvers]

    # Select the result with the highest value.
    # If two are tied, select the one with the shortest list of 'taken' items.
    (value, opt, taken_items) = max(results, key=lambda result_item: (result_item[0], -len(result_item[2])))
    taken_string = ' '.join(map(str, [(1 if i in taken_items else 0) for i in range(items_count)]))
    submission = f'{value} {opt}\n{taken_string}'
    print('\nSubmission:')
    return submission


if __name__ == '__main__':
    # Run the program on some data sets.
    for (prob_nbr, file_location) in enumerate(
        # This empty list lets you add other file names by uncommenting the lines below.
        []
        # These are first files in the data folder. They are both very small and good for a first test of your solver.
        # The homework sheet has a trace produced by an earlier version of the bb_solver.
        #                             Solution
        + ['./data/ks_4_0']         #    19
        # + ['./data/ks_6_0']         #    28

        # These are the data sets the system uses for testing. Add or comment out the ones you want/don't want to try.
        # Coursera numbers these data sets 1 - 6.
        #                                        Problem size   Time in seconds
        #                             Solution   in millions      bb      dp
        + ['./data/ks_30_0']       #    99798          3         0.17    0.02
        + ['./data/ks_50_0']       #   142156         17         0.00    0.00
        + ['./data/ks_200_0']      #   100236         20         0.55    0.17
        + ['./data/ks_400_0']      #  3967180       3795         2.88    0.59
        + ['./data/ks_1000_0']     #   109899        100         0.44    0.42
        + ['./data/ks_10000_0']    #  1099893      10000         4.61    1.98
        ):

        solvers = (bb_solver, dynamic_prog)

        # Reads a file and treat it as a single string.
        input_data = open(file_location, 'r').read()

        # If True, show the solvers used and the results they achieve
        verbose_outline = True

        # If True, show some of the details of how the solvers run.
        tracking_verbosity = False

        submission = solve_a_dataset(input_data, solvers, prob_nbr, verbose_outline, tracking_verbosity)

        # To run this for submission, you will have to get it to work as called by submit.py -- with no
        # additional output.
        print(submission)
