"""
Basic knapsack solvers: dynamic programming and various greedy solvers
"""

from collections import namedtuple
from copy import copy
from queue import PriorityQueue

from typing import List, Tuple


Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])
Selection = namedtuple('Selection', ['value', 'room', 'max_value', 'items_taken'])


def selection_str(selection):
    return f'Selection(value={selection.value}, room={selection.room}, max_value={round(selection.max_value, 2)})'


Neg_Room = Tuple[int]
Queue_Elt = Tuple[Neg_Room, Selection]


def dynamic_prog(greedy_value, items_count, capacity, density_sorted_items: List[Item], verbose_tracking):
    """
    Run the dynamic programming algorithm. It is right here!
    :param greedy_value:
    :param items_count:
    :param capacity:
    :param density_sorted_items:
    :param verbose_tracking
    :return:
    """
    # Keep only the current and most recent prev queues.
    # Each PriorityQueue, i.e., column, stores a Selection at each position ordered by available room: more to less.

    # verbose_tracking = True

    queue: PriorityQueue[Queue_Elt] = PriorityQueue()

    fut_density: float = density_sorted_items[0].density
    base_selection: Selection = Selection(value=0,
                                          room=capacity,
                                          max_value=capacity*density_sorted_items[0].density,
                                          items_taken=[])
    queue.put((-base_selection.room, base_selection))
    best_selection: Selection = Selection(value=greedy_value,
                                          room=0,
                                          max_value=capacity*density_sorted_items[0].density,
                                          items_taken=[])

    if verbose_tracking:
        print(f'item: {-1}; queue size: {0}; '
              f'fut_density: {round(fut_density, 5)}; best_selection: {selection_str(best_selection)}')

    for index in range(items_count):
        item: Item = density_sorted_items[index]
        prev_queue: PriorityQueue[Queue_Elt] = queue
        queue: PriorityQueue[Queue_Elt] = PriorityQueue()
        fut_density: float = 0 if index+1 >= items_count else density_sorted_items[index+1].density
        col_best_val = 0
        col_best_max_val = 0
        while not prev_queue.empty():
            (_, selection) = prev_queue.get()
            if selection.value < col_best_val or \
               selection.value == col_best_val and selection.max_value <= col_best_max_val:
                continue
            else:
                col_best_val = selection.value
                col_best_max_val = selection.max_value

            max_value = selection.value + selection.room * fut_density
            if max_value > best_selection.value:
                new_decline_selection = Selection(value=selection.value,
                                                  room=selection.room,
                                                  max_value=max_value,
                                                  items_taken=selection.items_taken)
                queue.put((-new_decline_selection.room, new_decline_selection))

            new_take_value = selection.value + item.value
            new_take_room = selection.room - item.weight
            new_take_selection = Selection(value=new_take_value,
                                           room=new_take_room,
                                           max_value=new_take_value + new_take_room * fut_density,
                                           items_taken=selection.items_taken + [index])

            if new_take_selection.max_value > best_selection.value and new_take_selection.room >= 0:
                queue.put((-new_take_selection.room, new_take_selection))
                if new_take_selection.value > best_selection.value:
                    best_selection = new_take_selection

        if verbose_tracking:
            print(f'item: {index}; queue size: {queue.qsize( )}; '
                  f'fut_density: {round(fut_density, 5)}; best_selection: {selection_str(best_selection)}')

    return (best_selection.value, best_selection.items_taken)


def dynamic_prog_original(_greedy_value, items_count, capacity, density_sorted_items, _verbose_tracking):
    """
    Run the dynamic programming algorithm. It is right here!
    :param _greedy_value:
    :param items_count:
    :param capacity:
    :param density_sorted_items:
    :param _verbose_tracking
    :return:
    """
    # Keep only the current and most recent prev column.
    # Each column stores a tuple at each position: (val, list_of_taken_elements)

    verbose_tracking = True

    col = [(0, [])]*(capacity+1)
    cur = col

    for i in range(items_count):
        prev = cur
        cur = copy(col)
        (index, value, weight, density) = density_sorted_items[i]
        for w in range(capacity+1):
            (p_val, p_elmts) = prev[w - weight] if weight <= w else (0, [])
            cur[w] = max(prev[w], (int(weight <= w) * (value + p_val), p_elmts + [i]),
                         key=lambda valElmts: valElmts[0])
        if verbose_tracking and items_count >= 1000:
            if i > 0 and i % 100 == 0:
                print(f'{i}/{items_count}', end=' ')
                if i % 1000 == 0:
                    print()
    if verbose_tracking and items_count >= 1000:
        print()

    return cur[capacity]
