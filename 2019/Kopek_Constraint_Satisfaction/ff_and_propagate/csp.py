# csp.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# Modified by Russ Abbott (2019)
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

from typing import Generic, Iterable, Dict, List, Optional, Set, Tuple, TypeVar
from abc import ABC, abstractmethod

V = TypeVar('V')  # variable type
D = TypeVar('D')  # domain type


# Base class for all constraints
class Constraint(Generic[V, D], ABC):
    # The variables that the constraint is between
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables

    # Must be overridden by subclasses
    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        ...

    # Must be overridden by subclasses
    @abstractmethod
    def propagate(self, next_var: int, next_var_value: int, unassigned: Dict[int, Set[int]]) -> Dict[int, Set[int]]:
        ...


def all_different(iterable: Iterable) -> bool:
    lst = list(iterable)
    st = set(lst)
    return len(lst) == len(st)


# A constraint satisfaction problem consists of variables of type V
# that have ranges of values known as domains of type D and constraints
# that determine whether a particular variable's domain selection is valid
class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, Set[D]]) -> None:
        self.variables: List[V] = variables  # variables to be constrained
        self.domains: Dict[V, Set[D]] = domains  # domain of each variable
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.low_mark = len(variables)
        self.count = 0
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    # noinspection PyDefaultArgument
    def backtracking_search(self, assignment: Dict[V, D], unassigned: Dict[V, Set[D]],
                            search_strategy='ff',
                            propagate_constraints=True,
                            check_constraints=True) -> Optional[Dict[V, D]]:
        # assignment is complete there are no unassigned variables left
        if not unassigned:
            return assignment

        # Print progress if at or below low-water mark.
        nbr_left = len(unassigned)
        if nbr_left <= self.low_mark:
            self.count += 1
            print(nbr_left, end='\n' if self.count % 20 == 0 else ' ')
            self.low_mark = nbr_left

        # select the variable to assign next. Default
        (next_var, next_var_domain) = select_next_var(search_strategy, unassigned)
        for value in next_var_domain:
            extended_assignment = assignment.copy()
            extended_assignment[next_var] = value
            next_unassigned = unassigned
            if propagate_constraints:
                for constraint in self.constraints[next_var]:
                    next_unassigned = constraint.propagate(next_var, value, next_unassigned)
            # if we're still consistent, we recurse (continue)
            if not check_constraints or self.consistent(next_var, extended_assignment):
                result: Optional[Dict[V, D]] = \
                                  self.backtracking_search(extended_assignment, next_unassigned,
                                                           search_strategy=search_strategy,
                                                           propagate_constraints=propagate_constraints,
                                                           check_constraints=check_constraints)
                # if we didn't find the result, we will end up backtracking
                if result is not None:
                    return result
        return None

    # Check if the value assignment is consistent by checking all constraints
    # for the given variable against it.
    # May not need this if we propagate_constraints. Then only consistent values remain in the domains.
    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

# @staticmethod
def select_next_var(strategy: str, unassigned: Dict[V, Set[D]]) -> Tuple[V, Set[D]]:
    if strategy == 'ff':  # strategy == fast_fail. Take the variable with the smallest remaining domain.
        next_var = min(unassigned, key=lambda v: len(unassigned[v]))
    else:  # strategy == 'default' Take the first unassigned variable
        next_var = [*unassigned.keys()][0]

    next_var_domain = unassigned[next_var]

    return (next_var, next_var_domain)
