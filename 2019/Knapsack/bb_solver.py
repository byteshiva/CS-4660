
"""
A straightforward Branch-and-Bound solver. Inspired by an Kevin Marlis' earlier BB solver.
"""
# You can read about namedtuples here: https://docs.python.org/3.7/library/collections.html#collections.namedtuple
from collections import namedtuple

# You can read about Python's Priority Queue here: https://dbader.org/blog/priority-queues-in-python
from queue import PriorityQueue
from random import randint
from typing import List


def bb_solver(_greedy_value, items_count, capacity, items_sorted_density, verbose_tracking):
    """
    Run the bb_solver.
    :param _greedy_value:
    :param items_count:
    :param capacity:
    :param items_sorted_density:
    :param verbose_tracking:
    :return:
    """
    # Note the pair of parentheses at the end of the next line. What do they do?
    return BBSolver(items_count, capacity, items_sorted_density, verbose_tracking)()


Selection = namedtuple('Selection', ['sorted_index', 'value', 'room', 'max_value', 'taken_sorted'])


class BBSolver:
    """
    A class to support dpbb knapsack solving.
    """

    def __init__(self, items_count, capacity, density_sorted_items, tracking_verbosity):
        self.items_count = items_count
        self.capacity = capacity
        self.sorted_items = density_sorted_items
        self.tracking_verbosity = tracking_verbosity
        self.pushes = 0
        self.frontier = PriorityQueue()
        self.expanded = {}

        # The following is a dummy element used to start building the queue.
        self.best_selection = Selection(sorted_index=-1, value=0, room=capacity,
                                         max_value=capacity*self.sorted_items[0].density, taken_sorted=[])
        # Expand self.best_selection to put the first two elements into the queue.
        # They are: take or don't take the first element of sorted_items.
        self.expand_and_enqueue(self.best_selection)

    def __call__(self):
        """
        This runs when an instance of BBSolver is called. See bb_solver in solver.py. Note the final ()
        :return:
        """
        high_index = self.items_count
        while not self.frontier.empty():
            self.print_frontier()
            # When we pull something off the frontier we get but don't use its priority.
            (_priority, selection) = self.frontier.get()
            if selection.sorted_index + 1 < self.items_count \
                and not self.already_expanded(selection) \
                and not self.too_small(selection):

                if self.tracking_verbosity and selection.sorted_index+1 < high_index:
                    if high_index < self.items_count:
                        print(f'Backtrack to: {selection.sorted_index+1}')
                    high_index = selection.sorted_index+1
                self.expand_and_enqueue(selection)
        return (self.best_selection.value, sorted(self.best_selection.taken_sorted))

    def already_expanded(self, selection):
        """
        Can we not expand this on the grounds that an equivalent or better selection has already been expanded?
        :return:
        """
        expanded_peers = self.expanded.get(selection.sorted_index, set())
        for (value, room) in expanded_peers:
            if selection.value <= value and selection.room <= room:
                if self.tracking_verbosity:
                    print(f'X-Already expanded-X {selection}: '
                          f'worse than already expanded value ({value}), weight ({room})')
                return True
        return False

    # noinspection PyMethodMayBeStatic
    @staticmethod
    def decline_next_item(selection: Selection, next_sorted_index, _next_sorted_item, future_density):
        """
        Don't include the next sorted item. The new Selection will be the same as the
        current one except with its sorted_index incremented to next_sorted_index.

        :param selection:
        :param next_sorted_index:
        :param _next_sorted_item:
        :param future_density:
        :return:
        """
        max_value = selection.value + selection.room * future_density
        next_selection = \
            Selection(sorted_index=next_sorted_index,
                      value=selection.value,
                      room=selection.room,
                      max_value=max_value,
                      taken_sorted=selection.taken_sorted)
        return next_selection

    def expand_and_enqueue(self, selection):
        """
        Expand selecction in two ways: include or don't include the next item in the sorted_items list.
        :param selection:
        """
        # Add this item's (value, room) to the expanded set.
        # Don't add anything for the initial selection, with sorted_index -1.
        if selection.sorted_index >= 0:
            self.expanded[selection.sorted_index] = \
                self.expanded.get(selection.sorted_index, set()) | {(selection.value, selection.room)}

        future_index = selection.sorted_index + 2

        future_density = 0 if future_index >= self.items_count else \
                         self.sorted_items[future_index].density

        next_sorted_index = selection.sorted_index + 1
        # This is the "next" item of the sorted_items linst. It may be included in the Selection.
        next_sorted_item = self.sorted_items[next_sorted_index]

        expanded_selections: List[Selection] = [fn(selection, next_sorted_index, next_sorted_item, future_density)
                                                for fn in [self.decline_next_item, self.take_next_item]]
        new_selections = [sel for sel in expanded_selections
                          if not self.too_heavy(sel) and not self.too_small(sel)]

        self.best_selection = max(new_selections + [self.best_selection],
                                  key=lambda selection: (selection.value, -selection.sorted_index))
        
        # We are now looking at the index of the newly generated selections. 
        # They both have the same sorted_index. 
        # If there is a next sorted_item to expand to, add them to the queue.
        if new_selections and new_selections[0].sorted_index + 1 < self.items_count:
            ordered_selections = new_selections if bool(randint(0, 1)) else reversed(new_selections)
            for selection in sorted(ordered_selections):
                self.pushes += 1
                self.frontier.put(self.prioritize(selection))
        elif self.tracking_verbosity:
            if new_selections:
                print(f'\nNot enqueing successors of {selection}.')
            else:
                print(f'\nNo viable successors of {selection}.')

    def print_frontier(self, n=15):
        """
        :param n: Maximum elements to print
        :return:
        """
        if not self.tracking_verbosity:
            return
        temp_queue = PriorityQueue()
        print(f'\nfrontier (capacity: {self.capacity})')
        while not self.frontier.empty() and n > 0:
            (priority, selection) = elt = self.frontier.get()
            print(f'{priority}: {selection}')
            temp_queue.put(elt)
            n -= 1
        print(f'  ==> Best: {self.best_selection}\n')
        while not temp_queue.empty():
            elt = temp_queue.get()
            self.frontier.put(elt)

    # noinspection PyMethodMayBeStatic
    def prioritize(self, selection: Selection):
        """
        Create a priority for the selection in various ways. Uncomment the one you want to use.
        When you select one or more, explain how it uses a Priority Queue to achieve the indicated result
        :param selection:
        :return: a priority
        """
        # Random
        # from random import random
        # return (random(), selection)
        
        # two versions of best first by density
        # return (0 if selection.value == 0 else selection.weight/selection.value, selection) # 200: 29 sec
        # return (float('inf') if selection.value == 0 else selection.weight/selection.value, selection) # 200: 10 sec

        # best first by value:
        # return (-selection.value, selection)

        # depth first:
        # return (-selection.sorted_index, selection)

        # breadth first (decline-first):
        # return ((selection.sorted_index, -selection.room), selection)

        # random choice breadth/depth first: 
        # from random import choice
        # return (choice([-1, 1]) * selection.sorted_index, selection)

        # LIFO:
        return (-self.pushes, selection)

        # FIFO:
        # return (self.pushes, selection)

    # noinspection PyMethodMayBeStatic
    @staticmethod
    def take_next_item(selection: Selection, next_sorted_index, next_sorted_item, future_density):
        """
        Include the next items from sorted_items in the selection. (See also decline_next_item.)
        :param selection:
        :param next_sorted_index:
        :param next_sorted_item:
        :param future_density:
        :return:
        """
        # Build the new Selection.
        next_selection_value = selection.value + next_sorted_item.value
        next_selection_room = selection.room - next_sorted_item.weight
        next_selection_max_value = next_selection_value + next_selection_room * future_density

        return Selection(sorted_index=next_sorted_index,
                         value=next_selection_value,
                         room=next_selection_room,
                         max_value=next_selection_max_value,
                         taken_sorted=selection.taken_sorted + [next_sorted_index])

    def too_heavy(self, selection: Selection):
        """
        Has this selection passed the capacity limit.  Selections keep track of room left rather than weight.
        So we have passe the capacity is room is less than 0.
        :return:
        """
        if selection.room < 0:
            if self.tracking_verbosity:
                print(f'X-Too heavy-X {selection}: '
                      f'selection.room ({selection.room}) < self.capacity ({self.capacity})')
            return True
        return False

    def too_small(self, selection):
        """
        Is this Selection worse than the best seen so far. If so, don't expand it.

        The more you can eliminate--and keep from being added to the queue, the
        faster the program will run. Is this the best way to test? It seems
        very ad hoc.

        :return:
        """
        """
           selection.max_value < self.best_selection.value \
           or \
           selection.max_value == self.best_selection.value and (
           selection.sorted_index < self.best_selection.sorted_index
           or
           selection.sorted_index >= self.best_selection.sorted_index and
           selection.value <= self.best_selection.value):
        """
        too_small = (
                     selection.max_value < self.best_selection.value
                     or
                     selection.max_value == self.best_selection.value
                     and selection.sorted_index >= self.best_selection.sorted_index
                    )
        if too_small and self.tracking_verbosity:
            print(f'X-Too small-X: {selection} vs\n'
                  f'               {self.best_selection})')
            return True
        return too_small
