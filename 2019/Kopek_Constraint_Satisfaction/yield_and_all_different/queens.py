# queens.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# Modified by Russ Abbott (July, 2019)
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from timeit import default_timer as timer
from typing import Dict, List

from yield_and_all_different.csp import all_different, Constraint
from yield_and_all_different.queens_display import display_solution


class QueensConstraint(Constraint):
    def __init__(self, column_position_var_ids: List[int]) -> None:
        # column_position_var_ids is defined in outer scope
        super().__init__(column_position_var_ids)
        self.column_position_var_ids: List[int] = column_position_var_ids

    def satisfied(self, cols_to_rows: Dict[int, int]) -> bool:
        all_different_rows = all_different(cols_to_rows.values( ))
        if not all_different_rows:
            return False

        all_different_right_diags = all_different(cols_to_rows[i] + i for i in cols_to_rows)
        if not all_different_right_diags:
            return False

        all_different_left_diags = all_different(cols_to_rows[i] - i for i in cols_to_rows)
        return all_different_left_diags


def n_queens(board_size=8, all_solutions=False):
    if all_solutions:
        from yield_and_all_different.csp_yield import CSP
    else:
        from yield_and_all_different.csp import CSP

    column_position_var_ids: List[int] = [i + 1 for i in range(board_size)]
    column_position_values: List[int] = [i + 1 for i in range(board_size)]
    rows: Dict[int, List[int]] = {column_pos_var_id: column_position_values.copy( )
                                  for column_pos_var_id in column_position_var_ids}
    csp: CSP = CSP(column_position_var_ids, rows)
    csp.add_constraint(QueensConstraint(column_position_var_ids))
    solution_nbr = 0
    timer_start = timer( )
    if all_solutions:
        for solution in csp.backtracking_search( ):
            solution_nbr += 1
            display_solution(solution, time_rounded(timer_start), solution_nbr)
            if input('Next? (y/n) > ') != 'y':
                return
            timer_start = timer( )
        if solution_nbr == 0:
            print('\nNo solutions.')
        print(f'Final search time: {time_rounded(timer_start)} sec.')
    else:
        solution = csp.backtracking_search( )
        if solution:
            display_solution(solution, time_rounded(timer_start))
        else:
            print('\nNo solutions.')


def time_rounded(timer_start, precision=3):
    return round(timer( ) - timer_start, precision)


if __name__ == "__main__":
    n_queens(board_size=20, all_solutions=False)  # about 11-12 sec for same solution