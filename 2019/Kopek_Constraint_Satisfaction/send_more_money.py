# send_more_money.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
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

# Modified by Russ Abbott (2019)

from typing import Dict, List

from csp import CSP


def digits_to_number(digits: List[int]) -> int:
    """
    Convert a sequence of digits into a number.
    E.g., digits_to_number([1, 2, 3]) -> 123
    """
    return int(''.join(map(str, digits)))


def send_more_money_constraint(_csp: CSP, _newly_assigned_variable, assignment: Dict[str, int]) -> bool:
    """

    :param _csp: not used
    :param _newly_assigned_variable:  Not used
    :param assignment: the current assignment
    :return: True/False: Is the current assignment consistent with the constraint?
             Consistent doesn't mean the problem is solved, only that
             the current assignment is not inconsistent with the constraint.
             (The current assignment may be consistent but incomplete.)
    """
    if set('SENDMORY') == set(assignment.keys()):
        # If all variables are assigned, do the numbers add  up?
        (s, e, n, d, m, o, r, y) = (assignment[x] for x in 'SENDMORY')
        return (digits_to_number([s, e, n, d]) + digits_to_number([m, o, r, e])) == digits_to_number([m, o, n, e, y])
    else:
        # Not all variables have been assigned. We are not checking any other form of consistency.
        # (all_different is checked by the all_different constraint.)
        # In particular, we are not checking to see, for example, whether the first column adds up.
        return True


def display_result(term_1, term_2, sum, solution, assignments):
    if solution is None:
        print(f"\nNo solution found after {assignments} assignments!")
        return

    print(f"\nSolution found after {assignments} assignments!")
    print(f'{solution}\n')

    term_1_solution = ''.join([str(solution[x]) for x in term_1])
    term_2_solution = ''.join([str(solution[x]) for x in term_2])
    sum_solution = ''.join([str(solution[x]) for x in sum])
    print(f'  {term_1} ->  {term_1_solution}')
    print(f'+ {term_2} ->  {term_2_solution}')
    print(f'{"-" * (len(sum) + 1)}    {"-" * (len(sum))}')
    print(f' {sum} -> {sum_solution}')


if __name__ == "__main__":
    variables = 'SENDMORY'
    digits = set(range(10))
    domains = {var: digits for var in variables}
    domains['S'] = domains['S'] - {0}  # What if we wrote: domains['S'] = {8, 9}

    # Set assignment_limit to 0 to turn off tracing. A positive number indicates
    # the number of assignments to allow (and to display) before quitting.
    assignment_limit = 0

    # Create the CSP object
    csp: CSP[str, int] = CSP(list(variables), domains, assignment_limit)
    csp.add_constraint(csp.all_different)
    csp.add_constraint(send_more_money_constraint)

    # The argument is an assignment used to start the process of assigning values to variables.
    # SInce 'M' must be 1, plug that into the initial assignment.
    solution = csp.complete_the_assignment({'M': 1})
    assignments = csp.assignments
    display_result('SEND', 'MORE', 'MONEY', solution, assignments)
