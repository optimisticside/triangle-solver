import math
import operator
import functools
from dataclasses import dataclass
from typing import Tuple, List, Optional


MaybeFloat = Optional[float]


class TriangleException(Exception):
    """Thrown during solving"""

    pass


@dataclass
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


@dataclass
class TriangleSolver:
    sides: Tuple[MaybeFloat, MaybeFloat, MaybeFloat]
    angles: Tuple[MaybeFloat, MaybeFloat, MaybeFloat]
    perimeter: MaybeFloat = None
    area: MaybeFloat = None

    def calculate_last_angle(self):
        """Calculates one last unknown angle"""
        for i in range(3):
            if t.angles[i] is not None:
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
                # a = b * sin(A) / a
                self.sides[j] = (
                    math.sin(self.angles[i]) * self.sides[i] / self.angles[j]
                )

    def calculate_two_angles(self):
        """When 2 sides and 1 angle are known"""
        for i in range(3):
            if self.angles[i] is None:
                continue

            if self.sides[i] is None:
                # Law of cosines: c^2 = a^2 + b^2 - 2ab cos(C)
                # c = sqrt(a^2 + b^2 - 2ab cos(C))
                a, b = rest(self.sides, i)
                self.sides[i] = math.sqrt(
                    a**2 + b**2 - 2 * a * b * math.cos(self.angles[i])
                )
        else:
            for j in range(3):
                if self.sides[j] is None:
                    continue
                # Law of sines: sin A / a = sin B / b
                # B = arcsin(b * sin A / a
                self.angles[j] = math.asin(
                    math.sin(self.angles[i]) * self.sides[j] / self.sides[i]
                )
                self.calculate_two_sides()

        self.calculate_three_angles()

    def calculate_three_angles(self):
        """When all 3 sides are known"""
        for i in range(3):
            # Law of Cosines: c^2 = a^2 + b^2 - 2ab cos(C)
            # C = arccos((a^2 + b^2 - c^2) / 2ab)
            a, b = rest(self.sides, i)
            self.angles[i] = math.acos(
                (a**2 + b**2 - self.sides[i] ** 2) / (2 * a * b)
            )

    def calculate_other(self):
        """Calculate other unrelated variables"""
        self.perimeter = sum(self.sides)
        # Heron's formula: A = sqrt(s(s - a)(s - b)(s - c)) where s = (a + b + c) / 2
        s = self.perimeter / 2
        self.area = functools.reduce(
            operator.mul, [s - x for x in self.sides], s
        )  # I thought I could do s * (s - x for x in t.sides)


def solve(sides: List[MaybeFloat], angles: List[MaybeFloat]) -> Optional[Triangle]:
    """Main solving routine"""
    side_count = len([x for x in sides if x is not None])
    angle_count = len([x for x in angles if x is not None])

    # validator = TriangleValidate(sides, angles)
    t = TriangleSolver(
        sides=ensure_size(sides, None, 3), angles=ensure_size(angles, None, 3)
    )

    if side_count == 3:
        t.calculate_three_angles()
    elif side_count == 2:
        t.calculate_two_angles()
    elif side_count == 1:
        t.calculate_two_sides()
    else:
        return None

    t.calculate_other()
    return Triangle(sides=t.sides, angles=t.angles, perimeter=t.perimeter, area=t.area)
