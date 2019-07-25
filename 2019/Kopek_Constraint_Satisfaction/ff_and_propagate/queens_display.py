from math import log10

from typing import Dict, Optional


def display_solution(solution: Dict[int, int], time: float, solution_nbr: Optional[int] = None) -> None:
    # The solver is 1-based; the display code assumes the solve is 0-based.
    if len(solution) <= 30:
        solution = {row-1: col-1 for (row, col) in solution.items()}
        sol = sorted([(r, c) for (r, c) in solution.items(  )])
        placement_vector = [c for (_, c) in sol]
        solution_display = layout(placement_vector)
        if solution_nbr:
            print(f'\n{solution_nbr}.', end='')
        print(f'\n{solution_display}', end='')
    print(f'\nTime: {time} sec.')


def layout(placement_vector: [int]) -> str:
    """ Format the placement_vector for display. """
    board_size = len(placement_vector)
    offset = ord('a')
    # Generate the column headers.
    col_hdrs = ' '*(4+int(log10(board_size))) + \
               '  '.join([f'{chr(n+offset)}' for n in range(board_size)]) + '  col#\n'
    display = col_hdrs + '\n'.join([one_row(r, c, board_size) for (r, c) in enumerate(placement_vector)])
    return display


def one_row(row: int, col: int, board_size: int) -> str:
    """ Generate one row of the board. """
    # (row, col) is the queen position expressed in 0-based indices.
    return f'{space_offset(row+1, board_size)}{row+1}) ' + \
           f'{" . "*col} Q {" . "*(board_size-col-1)} {space_offset(col+1, board_size)}({col+1})'


def space_offset(n: int, board_size: int) -> str:
    return " "*(int(log10(board_size)) - int(log10(n)))
