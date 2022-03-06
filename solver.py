import math
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


@dataclass
class IncompleteTriangle:
    """Used internally to store data while doing calcualtions"""
    sides: Tuple[MaybeFloat, MaybeFloat, MaybeFloat]
    angles: Tuple[MaybeFloat, MaybeFloat, MaybeFloat]


def ensure_size(arr: List, default, size: int) -> List:
    """Ensures the size of an array by using the default
    when an element does not exist.
    """
    return [arr[x] if x < len(arr) else default for x in range(size)]


def rest(arr: List, n: int) -> Tuple[int, int]:
    """Gets an array of the reamining elements of an array"""
    return [arr[x] for x in range(len(arr)) if x != n]


def calculate_last_angle(t: IncompleteTriangle):
    """Calculates one last unknown angle"""
    for i in range(3):
        if t.angles[i] is not None:
            continue
        a, b = rest(t.angles, i)
        t.angles[i] = math.pi - (a + b)


def calculate_two_sides(t: IncompleteTriangle):
    """When at least 1 side and 2 angles are known"""
    calculate_last_angle(t)
    for i in range(3):
        if t.sides[i] is None:
            continue
        for j in range(3):
            if t.sides[j] is not None:
                continue
            # Law of sines: sin(A) / a = sin(B) / b
            # a = b * sin(A) / a
            t.sides[j] = math.sin(t.angles[i]) * t.sides[i] / t.angles[j]


def calculate_two_angles(t: IncompleteTriangle):
    """When 2 sides and 1 angle are known"""
    for i in range(3):
        if t.angles[i] is None:
            continue

        if t.sides[i] is None:
            # Law of cosines: c^2 = a^2 + b^2 - 2ab cos(C)
            # c = sqrt(a^2 + b^2 - 2ab cos(C))
            a, b = rest(t.sides, i)
            t.sides[i] = math.sqrt(a**2 + b**2 - 2 * a * b * math.cos(t.angles[i]))
        else:
            for j in range(3):
                if t.sides[j] is None:
                    continue
                # Law of sines: sin A / a = sin B / b
                # B = arcsin(b * sin A / a
                t.angles[j] = math.asin(
                    math.sin(t.angles[i]) * t.sides[j] / t.sides[i]
                )
                calculate_two_sides(t)

    calculate_three_angles(t)


def calculate_three_angles(t: IncompleteTriangle):
    """When all 3 sides are known"""
    for i in range(3):
        # Law of Cosines: c^2 = a^2 + b^2 - 2ab cos(C)
        # C = arccos((a^2 + b^2 - c^2) / 2ab)
        a, b = rest(t.sides, i)
        t.angles[i] = math.acos((a**2 + b**2 - t.sides[i]**2) / (2 * a * b))


def solve(sides: List[MaybeFloat], angles: List[MaybeFloat]) -> Optional[Triangle]:
    """Main solving routine"""
    side_count = len([x for x in sides if x is not None])
    angle_count = len([x for x in angles if x is not None])

    # validate(sides, angles)
    if side_count + angle_count != 3:
        raise TriangleException("Only 3 numbers must be provided")

    t = IncompleteTriangle(
        sides=ensure_size(sides, None, 3), angles=ensure_size(angles, None, 3)
    )

    if side_count == 3:
        calculate_three_angles(t)
    elif side_count == 2:
        calculate_two_angles(t)
    elif side_count == 1:
        calculate_two_sides(t)
    else:
        return None

    return Triangle(sides=t.sides, angles=t.angles)

