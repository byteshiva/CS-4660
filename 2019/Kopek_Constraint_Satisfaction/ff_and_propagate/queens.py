# queens.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# Modified by Russ Abbott (Jouy, 2019)
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
from typing import Dict, List, Set

# from csp import all_different, Constraint, CSP
from csp_yield import all_different, Constraint, CSP
from queens_display import display_solution


class QueensConstraint(Constraint):
    def __init__(self, column_vars: List[int]) -> None:
        super().__init__(column_vars)
        self.column_vars: List[int] = column_vars

    def propagate(self, next_var: int, next_var_value: int, unassigned: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
        next_unassigned = {var_i: self.reduce_domain(next_var, next_var_value, var_i, var_i_domain)
                           for (var_i, var_i_domain) in unassigned.items( ) if var_i != next_var}
        return next_unassigned

    @staticmethod
    def reduce_domain(next_var, next_var_value, var_i, var_i_domain):
        diff = abs(next_var - var_i)
        return var_i_domain - {next_var_value, next_var_value + diff, next_var_value - diff}

    def satisfied(self, cols_to_rows: Dict[int, int]) -> bool:
        all_different_rows = all_different(cols_to_rows.values())
        if not all_different_rows:
            return False

        all_different_right_diags = all_different(cols_to_rows[i]+i for i in cols_to_rows)
        if not all_different_right_diags:
            return False

        all_different_left_diags = all_different(cols_to_rows[i]-i for i in cols_to_rows)
        return all_different_left_diags


def n_queens(board_size=8, search_strategy='ff', propagate_constraints=True, check_constraints=False):
    column_vars: List[int] = [i + 1 for i in range(board_size)]
    row_values: List[int] = [i + 1 for i in range(board_size)]
    column_domains: Dict[int, Set[int]] = {column_var: set(row_values) for column_var in column_vars}
    csp: CSP = CSP(column_vars, column_domains)
    csp.add_constraint(QueensConstraint(column_vars))
    solution_nbr = 0
    timer_start = timer( )
    for solution in csp.backtracking_search({}, column_domains,
                                            search_strategy=search_strategy,
                                            propagate_constraints=propagate_constraints,
                                            check_constraints=check_constraints):
        solution_nbr += 1
        display_solution(solution, time_rounded(timer_start), solution_nbr)
        if input('Next? (y/n) > ') != 'y':
            return
        timer_start = timer( )
    if solution_nbr == 0:
        print('\nNo solutions.')
    else:
        print(f'\nNo more solutions. Total solutions: {solution_nbr}')
    print(f'Final search time: {time_rounded(timer_start)} sec.')


def time_rounded(timer_start, precision=3):
    return round(timer( ) - timer_start, precision)


if __name__ == "__main__":

    # Time about 0.001 - 0.002 sec
    n_queens(board_size=20, search_strategy='ff', propagate_constraints=True, check_constraints=True)
