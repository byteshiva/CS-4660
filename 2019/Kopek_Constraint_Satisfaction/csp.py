# csp.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# With relatively minor modifications by Russ Abbott (7/2019)
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


# The first import allows the use of CSP as a type in all_different, a method within CSP.
# It shouldn't be necessary in Python 3.8
from __future__ import annotations

from typing import Callable, Dict, Generator, Generic, List, Optional, Set, TypeVar

V = TypeVar('V')  # the type of the variables
D = TypeVar('D')  # the type of the domain elements


class CSP(Generic[V, D]):
    """
    A constraint satisfaction problem consists of 
        a) variables of type V that have 
        b) domains of values of type D and 
        c) constraints that determine the validity of a given assignment of values to variables.  
    """
    
    def __init__(self, variables: List[V], domains: Dict[V, Set[D]], assignment_limit=0) -> None:
        self.variables: List[V] = variables  # the variables to be constrained
        self.domains: Dict[V, Set[D]] = domains  # the domain of each variable
        self.constraints: List[Callable[..., bool]] = []
        
        # Keeps track of the number of assignments created
        self.assignment_limit = assignment_limit
        self.assignments = 0
        self.printed_reached_limit = False

    def add_constraint(self, constraint: Callable[..., bool]) -> None:
        self.constraints.append(constraint)

    @staticmethod
    def all_different(_csp: CSP, _newly_assigned_variable, assignment: Dict[V, D]):
        """
        Are all values in the assignment unique?
        
        This is such a common constraint that we are including it here.
        """
        return len(set(assignment.values())) == len(assignment)

    def complete_the_assignment(self, assignment: Dict[V, D]) -> Optional[Dict[V, D]]:
        """
        Add variable/value pairs to assignment until it either fails a consistsency check if satisfies the constraints.
        :param assignment:
        :return: a consistent assignment or None if no extention assignment satisfies the constraints.
        """

        # Make a generator that returns all variables that have not yet been assigned values.
        # A generator is like a list comprehension but one that returns values as needed.
        # It's a form of lazy evaluation.
        unassigned_variables: Generator[V] = (v for v in self.variables if v not in assignment)
        # We use only the first variable. There was no need to generate all of them.
        selected_variable: V = next(unassigned_variables)  

        # Try all possible domain values of the selected variable
        for selected_value in self.domains[selected_variable]:


            # Extend the current assignment with: selected_variable: selected_value.
            # **assignment lists the elements of assignment.
            # So the following line creates a new dictiony with all the elements of
            # assignment plus the assignment to selected_variable.  selected_variable: selected_value
            extended_assignment = {**assignment, selected_variable: selected_value}
            self.assignments += 1

            if self.assignment_limit:
                if self.assignments <= self.assignment_limit:
                    print((f'{self.assignments:2}' if self.assignments < 100 else f'{self.assignments}') +
                          f'. {extended_assignment}')
                else:
                    if not self.printed_reached_limit:
                        print(f'Reached the assignment_limit of {self.assignment_limit}. ')
                        self.printed_reached_limit = True
                    self.assignments = self.assignment_limit
                    return None

            if not self.is_consistent(selected_variable, extended_assignment):
                continue

            # The assignment is consistent with the constraints. Is it complete?
            # An assignment is complete if every variable is assigned a value.
            # The next line is True only when we have just added the final variable/value combination to assignment.
            if len(extended_assignment) == len(self.variables):
                return extended_assignment

            # The assignment is consistent but not complete.
            # Use recursion to complete the assignment.
            # result will be either a valid assignment or None if no valid completion is found.
            result = self.complete_the_assignment(extended_assignment)

            # result is None if we didn't find a valid assignment for the remaining variables.
            # In that case, try the next value for selected_variable.
            if result is None:
                continue

            # result is a valid assignment. Return it.
            return result

        # If no value for selected_variable yields a valid assignment, return None and
        # let the previous recursive level try the next value for its variable.
        return None

    def is_consistent(self, newly_assigned_variable, assignment: Dict[V, D]) -> bool:
        """
        Is assignment consistent with all constraints?
        """
        return all(constraint(self, newly_assigned_variable, assignment) for constraint in self.constraints)
