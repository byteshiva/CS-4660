
from copy import copy
from queue import PriorityQueue
from random import choice
from time import time
from typing import Dict, List, Callable, Set, Tuple

# Define a type alias for the board.
# The board is represented as a dictionary where the keys are (row, col)
# tuples and the values are the values at those positions.
Board_Dict = Dict[Tuple[int, int], int]


# noinspection PyRedundantParentheses
# I prefer writing (x, y) to x, y. Either is syntactically valid.
class FifteenPuzzle:

    def __init__(self):
        goal_array = ((1, 2, 3, 4),
                      (5, 6, 7, 8),
                      (9, 10, 11, 12),
                      (13, 14, 15, 0))
        self.nbr_of_rows = self.nbr_of_cols = len(goal_array)
        self.goal_dict = self.board_array_to_board_dict(goal_array)
        # The inverse-goal_dict tells you the correct (row, col) position of any value.
        self.inverse_goal_dict: Dict[int, Tuple[int, int]] = {val: row_col for (row_col, val) in self.goal_dict.items()}

    # noinspection PyUnusedLocal
    def a_star_search(self, start: Board_Dict, search_type: str = None, max_expanded_nodes: int = None) \
                                                                                    -> Tuple[int, List[Board_Dict]]:
        """
        A* search search
        :param search_type: Not used
        :param start: An initial Board state in the form of a Board_Dict
        :param max_expanded_nodes: not used
        :return: (expanded nodes count, the path)
        """
        path = None
        frontier_puts = 0
        frontier = PriorityQueue()
        # The frontier is a PriorityQueue with elements of the form Tuple[(int, int) List[Board_Dict)]]
        # The first element of the tuple is itself a tuple: (Manhattan_distance + path_length, put_count).
        # The put_count distinguishes between two paths with the same Manhattan distance and same length.
        # The second element of the tuple is a path, i.e., a list of boards
        min_man_dist = self.man_dist(start)
        frontier.put(((min_man_dist + 2, frontier_puts), [start]))
        print(f'min_man_dist (queue size): {min_man_dist}({frontier.qsize()})', end=' ')
        print_counter = 1
        frontier_puts += 1
        # The set of expanded nodes is stored as strings so that it can be a set.
        expanded: Set[str] = set()
        # The number of nodes that have been expanded.
        expanded_nodes_count = 0
        while not frontier.empty():
            (_, path) = frontier.get()
            end_node = path[-1]
            # Dictionaries can be compared in this way.
            if end_node == self.goal_dict:
                break
            end_node_str = self.board_to_str(end_node)
            if end_node_str in expanded:
                continue
            for neighbor in self.neighbors(end_node):
                if self.board_to_str(neighbor) in expanded:
                    continue
                new_man_dist = self.man_dist(neighbor)
                newpath = ((new_man_dist + len(path) + 1,  frontier_puts), path + [neighbor])
                frontier.put(newpath)
                frontier_puts += 1
                if new_man_dist < min_man_dist:
                    print(f'{new_man_dist}({frontier.qsize()})', end=' ')
                    print_counter += 1
                    if min_man_dist > 0 and print_counter % 10 == 0:
                        print(f'\nmin_man_dist (queue size): ', end='')
                    min_man_dist = new_man_dist
            # update() expects a collection of things to add to the set.
            # In this case the collection is a list of one thing.
            expanded.update([end_node_str])
            expanded_nodes_count += 1
        return (expanded_nodes_count, path)

    def board_array_to_board_dict(self, board_array):
        goal_dict: Board_Dict = {(row, col): board_array[row][col]
                                      for row in range(self.nbr_of_rows)
                                      for col in range(self.nbr_of_cols)}
        return goal_dict

    def board_to_str(self, puzzle_board: Board_Dict) -> str:
        """ Turn a board into a string that represents it.
        :param puzzle_board: Board_Dict the current state of the board
        :return A string representation of the board suitable for hashing.
        """
        ordered_values = ','.join([str(puzzle_board[key]) for key in self.goal_dict.keys()])
        return ordered_values

    def bds_dfs(self, start: Board_Dict, search_type: str, max_expanded_nodes: int) -> Tuple[int, List[Board_Dict]]:
        """ Breadth-first or depth-first search -- with ordered neighbors
        :param search_type: 'bfs' or 'dfs'
        :param max_expanded_nodes: The maximum number of nodes to allow to be expanded before quitting.
        :param start: Board_Dict: the starting state for the search
        :return (expanded nodes count, (A* value, The path))
        """
        path = None
        frontier = [(self.man_dist(start), [start])]
        print(f'expanded_nodes (out of {max_expanded_nodes})(queue size): ', end=' ')
        expanded: Set[str] = set()
        expanded_nodes = 0
        while frontier:
            ((_, path), frontier) = (frontier[0], frontier[1:])
            end_node = path[-1]
            if end_node == self.goal_dict:
                break
            end_node_str = self.board_to_str(end_node)
            if end_node_str in expanded:
                continue
            # Sort in reverse for dfs because we push the sorted elements into the Frontier.
            # Want to push the worst first and the best last so that the best is at the
            # front of the frontier.
            for (md, neighbor) in self.sorted_neighbors(end_node, reverse=(search_type == 'dfs')):
                if self.board_to_str(neighbor) in expanded:
                    continue
                insertion_position = 0 if search_type == 'dfs' else len(frontier)
                frontier.insert(insertion_position, (md, path + [neighbor]))
            expanded.update([end_node_str])
            expanded_nodes += 1
            if expanded_nodes % 5000 == 0:
                print(f'{expanded_nodes}({len(frontier)})', end=' ')
                if expanded_nodes < max_expanded_nodes and expanded_nodes % 25000 == 0:
                    print(f'\nexpanded_nodes (out of {max_expanded_nodes})(queue size): ', end=' ')
            if expanded_nodes > max_expanded_nodes:
                (_, path) = min(frontier, key=lambda md_path: md_path[0])
                break
        return (expanded_nodes, path)

    @staticmethod
    def find_the_blank(puzzle_board: Board_Dict) -> Tuple[int, int]:
        """ Finds where the blank (represented by 0) is.
        :param puzzle_board: The current state of the puzzle_board
        :return: the (row, col) of tile 0.
        """
        for (row_col, val) in puzzle_board.items():
            if val == 0:
                return row_col

    def man_dist(self, puzzle_board: Board_Dict) -> int:
        """
        :param puzzle_board: Board_Dict; the current state of the board
        :returns: the total Manhattan distance of the tiles on the board
        """
        total_man_dist = 0
        for ((row, col), val) in puzzle_board.items():
            # Don't count the dist of 0 from its goal position.
            if val > 0:
                (goal_row, goal_col) = self.inverse_goal_dict[val]
                tile_dist = abs(row - goal_row) + abs(col - goal_col)
                total_man_dist += tile_dist
        return total_man_dist

    # noinspection PyIncorrectDocstring
    @staticmethod
    def move_blank(puzzle_board: Board_Dict, from_row, from_col, to_row, to_col) -> Board_Dict:
        """
        :param (from_row, from_col): the current position of the empty space.
        :param (to_row, 7o_col): the position to which the empty space is to be moved.
        :param puzzle_board: Board_Dict; the current state of the board
        :returns: a copy of the puzzle_board with the empty space moved as indicated.
        """
        new_puzzle_board: Board_Dict = copy(puzzle_board)
        # Move the tile from the destination of the blank to the current blank location.
        new_puzzle_board[(from_row, from_col)] = puzzle_board[(to_row, to_col)]
        new_puzzle_board[(to_row, to_col)] = 0
        return new_puzzle_board

    def neighbors(self, puzzle_board: Board_Dict) -> List[Board_Dict]:
        """
        Returns a list of all puzzle_board neighbors
        :parameter: puzzle_board: Board_Dict; the current state of the board
        :returns: a List[Board_Dict] of possible successor states.
        """
        (row, col) = self.find_the_blank(puzzle_board)
        neighbrs = [self.move_blank(puzzle_board, row, col, row+row_delta, col+col_delta)
                    for (row_delta, col_delta) in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= row+row_delta <= 3 and 0 <= col+col_delta <= 3]
        # assert None not in neighbrs
        return neighbrs

    def print_board(self, board: Board_Dict):
        """
        Print the board in a pretty format
        :param board: Board_Dict; the current state of the board
        """
        # Extract the rows from the Board_Dict
        rows: List[List[int]] = [[board[(row, col)] for col in range(self.nbr_of_cols)]
                                 for row in range(self.nbr_of_rows)]
        for row in rows:
            self.print_row(row)
        print()

    def print_result(self, srch_name: str, expanded_nodes: int, time: float, path: List[Board_Dict]):
        """
        Print the results of the search
        :param srch_name: The name of the search
        :param expanded_nodes: The number of nodes that were expanded
        :param time: The time taken by the search
        :param path: The path returned by the search.
        """
        for (i, board) in enumerate(path):
            pos = i+1
            md = self.man_dist(board)
            print(f'{pos}+{md}={pos+md}.')
            self.print_board(board)
        print(f'{srch_name} search')
        print(f'Expanded nodes: {expanded_nodes}')
        print(f'Elapsed time: {round(time, 2)} sec')
        print(f'Path length: {len(path)}.\n')

    @staticmethod
    def print_row(row: List[int]):
        """
        Print a row of the board
        :param row:
        """
        elts = [' __' if n == 0 else f'  {n}' if n < 10 else f' {n}' for n in row]
        string = ' '.join(elts)
        print(string)

    @staticmethod
    def run_puzzle(srch_name: str, start: Board_Dict,
                   search_algo: Callable[[Board_Dict, str, int], Tuple[int, List[Board_Dict]]],
                   search_type: str = None,
                   max_expanded_nodes: int = -1) -> int:
        """
        Run the indicated search and display the results.

        :param search_type: The search type if 'bfs' or 'dfs'
        :param srch_name: The printable name of the search
        :param start: The starting board position
        :param search_algo: the search algorithm
        :param max_expanded_nodes: the maximum number of nodes to be expanded
        :return: the actual number of nodes expanded
        """
        print(f'{" "*10}{".   "*20}.')
        print(f'{" "*10}{" . ."*20}')
        print(f'{" "*10}{"  . "*20}')
        print(f'\nStarting {srch_name} search with: ')
        puzzle.print_board(start)
        start_time = time()
        (expanded_nodes, path) = search_algo(start, search_type, max_expanded_nodes)
        print('\n')
        puzzle.print_result(srch_name, expanded_nodes, time() - start_time, path)
        return expanded_nodes

    def shuffle(self, steps: int) -> Board_Dict:
        """
        Shuffle the board to start the game.
        :param steps: The number of quasi-random moves to make from the solved state.
        :return A shuffled Board.
        """
        puzzle_board: Board_Dict = self.goal_dict
        for i in range(steps):
            sorted_neighbors = self.sorted_neighbors(puzzle_board, reverse=True)
            # Select randomly one of the two most disordered.
            puzzle_board = choice(sorted_neighbors[:2])[1]
        return puzzle_board

    def sorted_neighbors(self, puzzle_board, reverse: bool = False) -> List[Tuple[int, Board_Dict]]:
        """
        Generate and sort by man_dist the neighbors of puzzle_board
        :param puzzle_board:
        :param reverse: True -> sort High-to-low
        :return: A list of neighbors of puzzle-board sorted by man_dist
        """
        # Work with tuples of (man_dist, board_dict)
        md_neighbors: List[Tuple[int, Board_Dict]] = [(self.man_dist(n), n) for n in self.neighbors(puzzle_board)]
        # Sort the neighbors by man_dist.
        sorted_md_neighbors = sorted(md_neighbors, key=lambda md_n: md_n[0], reverse=reverse)
        return sorted_md_neighbors


if __name__ == '__main__':
    puzzle = FifteenPuzzle()

    # Start with either a randomly generate board or a specified one.

    # Use a randomly generated board
    # shuffle_steps = 17
    # start: Board_Dict = puzzle.shuffle(shuffle_steps)

    # Use a specific board.
    # Given the following start board:
    #
    # A* search
    # Expanded nodes: 20
    # Elapsed time: 0.0 sec
    # Path length: 16.
    #
    # Depth-first search
    # Expanded nodes: 2631
    # Elapsed time: 0.22 sec
    # Path length: 2632.
    #
    # Breadth-first search
    # Expanded nodes: 100001
    # Elapsed time: 116.22 sec
    # Path length: 16.

    puzzle_board = ((2, 3, 11, 4),
                    (1, 5, 15, 7),
                    (9, 0,  6, 8),
                    (13, 10, 14, 12))

    # noinspection PyRedeclaration
    start = puzzle.board_array_to_board_dict(puzzle_board)

    expanded_nodes = puzzle.run_puzzle('A*', start, puzzle.a_star_search)
    puzzle.run_puzzle('Depth-first', start, puzzle.bds_dfs, 'dfs', min(500000, 10000*expanded_nodes))
    puzzle.run_puzzle('Breadth-first', start, puzzle.bds_dfs, 'bfs', min(500000, 10000*expanded_nodes))
