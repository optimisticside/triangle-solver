"""Triangle Solver

This module allows solving a triangle being give only three variables.
It uses formulas such as the law of sines and law of cosines to calculate
the other variables of the triangle, as well as additional things like
its area and perimeter.

It contains `solve`, which is the main function to solve a triangle,
which internally will use the `TriangleSolver` class.

Before solving, the triangle is validated. If the triangle is invalid,
a `TriangleException` will be raised with an an error that can be found
in the `TriangleError` enum.
"""

from __future__ import annotations
import math
import operator
import functools
import dataclasses
from enum import Enum
from typing import Tuple, List, Optional


MaybeFloat = Optional[float]


class TriangleException(Exception):
    """Thrown during solving"""


@dataclasses.dataclass
class Triangle:
    """Complete triangle structure.
    Returned by solve function.
    """

    sides: Tuple[float, float, float]
    angles: Tuple[float, float, float]
    perimeter: float
    area: float


def ensure_size(arr: List, default, size: int) -> List:
    """Ensures the size of an array by using the default
    when an element does not exist.
    """
    return [arr[x] if x < len(arr) else default for x in range(size)]


def rest(arr: List, n: int) -> Tuple[int, int]:
    """Gets an array of the reamining elements of an array"""
    return [arr[x] for x in range(len(arr)) if x != n]


class TriangleError(Enum):
    """Supplied when throwing a TriangleException"""

    NOT_ENOUGH_VARIABLES = 1
    TOO_MANY_VARIABLES = 2
    NO_SIDES = 3
    INVALID_SIDE = 4
    INVALID_ANGLE = 5
    INVALID_TRIANGLE = 6


@dataclasses.dataclass
class TriangleSolver:
    """Main solving class for triangle solver.
    Used in solve() function.
    """

    sides: List[MaybeFloat]
    angles: List[MaybeFloat]
    is_alternative = False
    alternatives: Optional[TriangleSolver] = None
    perimeter: MaybeFloat = None
    area: MaybeFloat = None

    def validate_side(self, i: int) -> bool:
        """Checks if a side is valid"""
        a, b = rest(self.sides, i)
        return (a is None or b is None) or (self.sides[i] < a + b and self.sides[i] > abs(a - b))

    def validate_angle(self, i: int) -> bool:
        """Checks if an angle is valid"""
        return self.angles[i] < math.pi

    def validate(self, complete=False):
        """Validates the triangle and throws
        a TriangleException if an error is found
        """
        for i in range(3):
            if self.sides[i] is not None and not self.validate_side(i):
                raise TriangleException(TriangleError.INVALID_SIDE)

            if self.angles[i] is None:
                continue

            if not self.validate_angle(i):
                raise TriangleException(TriangleError.INVALID_ANGLE)

            if not complete:
                continue

            # Law of Cosines: c^2 = a^2 + b^2 - 2ab cos(C)
            # C = arccos((a^2 + b^2 - c^2) / 2ab)
            a, b = rest(self.sides, i)
            angle = math.acos((a**2 + b**2 - self.sides[i] ** 2) / (2 * a * b))
            if math.isclose(angle, self.angles[i]):
                raise TriangleException(TriangleError.INVALID_TRIANGLE)

        side_count = len([x for x in self.sides if x is not None])
        angle_count = len([x for x in self.angles if x is not None])

        if side_count + angle_count > 3:
            raise TriangleException(TriangleError.TOO_MANY_VARIABLES)

        if side_count + angle_count < 3:
            raise TriangleException(TriangleError.NOT_ENOUGH_VARIABLES)

        if side_count == 0:
            raise TriangleException(TriangleError.NO_SIDES)

    def is_ambigous(self, a: int, b: int) -> bool:
        """Determines if there are two solutions to the problem"""
        return (
            self.angles[b] < math.pi / 2
            and self.sides[a] < self.sides[b]
            and self.sides[a] > self.sides[b] * math.sin(self.angles[a])
        )

    def calculate_last_angle(self):
        """Calculates one last unknown angle"""
        for i in range(3):
            if self.angles[i] is not None:
                continue

            a, b = rest(self.angles, i)
            self.angles[i] = math.pi - (a + b)

    def calculate_two_sides(self):
        """When at least 1 side and 2 angles are known"""
        self.calculate_last_angle()
        for i in range(3):
            if self.sides[i] is None:
                continue

            for j in range(3):
                if self.sides[j] is not None:
                    continue
                # Law of sines: sin(A) / a = sin(B) / b
                # b = a * sin(B) / sin(A)
                self.sides[j] = math.sin(self.angles[j]) * self.sides[i] / math.sin(self.angles[i])

    def calculate_two_angles(self):
        """When 2 sides and 1 angle are known"""
        for i in range(3):
            if self.angles[i] is None:
                continue

            if self.sides[i] is None:
                # Law of cosines: c^2 = a^2 + b^2 - 2ab cos(C)
                # c = sqrt(a^2 + b^2 - 2ab cos(C))
                a, b = rest(self.sides, i)
                self.sides[i] = math.sqrt(a**2 + b**2 - 2 * a * b * math.cos(self.angles[i]))
                self.calculate_three_angles()
            else:
                for j in range(3):
                    if self.sides[j] is None or i == j:
                        continue
                    # Law of sines: sin A / a = sin B / b
                    # B = arcsin(b * sin A / a)
                    self.angles[j] = math.asin(math.sin(self.angles[i]) * self.sides[j] / self.sides[i])

                    if self.is_ambigous(i, j) and not self.is_alternative:
                        copy = dataclasses.replace(self)
                        copy.angles[j] = math.pi - self.angles[j]
                        copy.calculate_two_sides()

                        copy.validate(True)
                        copy.calculate_other()
                        self.alternative = copy

                    self.calculate_two_sides()

    def calculate_three_angles(self):
        """When all 3 sides are known"""
        for i in range(3):
            # Law of Cosines: c^2 = a^2 + b^2 - 2ab cos(C)
            # C = arccos((a^2 + b^2 - c^2) / 2ab)
            a, b = rest(self.sides, i)
            self.angles[i] = math.acos((a**2 + b**2 - self.sides[i] ** 2) / (2 * a * b))

    def calculate_other(self):
        """Calculate other unrelated variables"""
        self.perimeter = sum(self.sides)
        # Heron's formula: A = sqrt(s(s - a)(s - b)(s - c)) where s = (a + b + c) / 2
        s = self.perimeter / 2
        self.area = functools.reduce(
            operator.mul, [s - x for x in self.sides], s
        )  # I thought I could do s * (s - x for x in t.sides)

    def solve(self):
        """Solves the triangle"""
        self.validate()
        side_count = len([x for x in self.sides if x is not None])

        if side_count == 3:
            self.calculate_three_angles()
        elif side_count == 2:
            self.calculate_two_angles()
        elif side_count == 1:
            self.calculate_two_sides()

        self.validate(True)
        self.calculate_other()


def solve(sides: List[MaybeFloat], angles: List[MaybeFloat]) -> Optional[Triangle]:
    """Main solving routine"""
    solver = TriangleSolver(sides=ensure_size(sides, None, 3), angles=ensure_size(angles, None, 3))

    solver.solve()
    return Triangle(
        sides=solver.sides,
        angles=solver.angles,
        perimeter=solver.perimeter,
        area=solver.area,
    )
