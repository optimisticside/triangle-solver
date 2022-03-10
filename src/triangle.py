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

import math


class TriangleException(Exception):
    """Thrown during solving"""


class Triangle:
    """Complete triangle structure.
    Returned by solve function.
    """

    def __init__(self, sides, angles, altitudes, medians, perimeter, area):
        self.sides = sides
        self.angles = angles
        self.altitudes = altitudes
        self.medians = medians
        self.perimeter = perimeter
        self.area = area


def ensure_size(arr, default, size):
    """Ensures the size of an array by using the default
    when an element does not exist.
    """
    return [arr[x] if x < len(arr) else default for x in range(size)]


def rest(arr, n):
    """Gets an array of the reamining elements of an array"""
    return [arr[x] for x in range(len(arr)) if x != n]


class TriangleError:
    """Supplied when throwing a TriangleException"""

    NOT_ENOUGH_VARIABLES = 1
    TOO_MANY_VARIABLES = 2
    NO_SIDES = 3
    INVALID_SIDE = 4
    INVALID_ANGLE = 5
    INVALID_TRIANGLE = 6


class TriangleSolver:
    """Main solving class for triangle solver.
    Used in solve() function.
    """

    sides = None
    angles = None
    altitudes = None
    medians = None
    is_alternative = False
    alternative = None
    perimeter = None
    area = None

    def __init__(self, sides=[], angles=[], is_alternative=False):
        self.sides = sides
        self.angles = angles
        self.altitudes = [None] * 3
        self.medians = [None] * 3
        self.is_alternative = is_alternative

    def validate_side(self, i):
        """Checks if a side is valid"""
        a, b = rest(self.sides, i)
        return (a is None or b is None) or (self.sides[i] < a + b and self.sides[i] > abs(a - b))

    def validate_angle(self, i):
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
            if not math.isclose(angle, self.angles[i], abs_tol=0.01):
                raise TriangleException(TriangleError.INVALID_TRIANGLE)

        side_count = len([x for x in self.sides if x is not None])
        angle_count = len([x for x in self.angles if x is not None])

        if not complete:
            if side_count + angle_count > 3:
                raise TriangleException(TriangleError.TOO_MANY_VARIABLES)

            if side_count + angle_count < 3:
                raise TriangleException(TriangleError.NOT_ENOUGH_VARIABLES)

            if side_count == 0:
                raise TriangleException(TriangleError.NO_SIDES)

    def is_ambigous(self, a, b):
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
                        copy = TriangleSolver()
                        copy.is_alternative = True
                        copy.angles = list(self.angles)
                        copy.sides = list(self.sides)
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
        self.area = s * (s - self.sides[0]) * (s - self.sides[1]) * (s - self.sides[2])
        for i in range(3):
            a, b = rest(range(3), i)
            self.altitudes[i] = math.sin(self.angles[a]) * self.sides[b]
            self.medians[i] = math.sqrt((self.sides[a] ** 2 + self.sides[b] ** 2 - self.sides[i] ** 2 / 2) / 2)

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


def display(triangle):
    sides = [round(x, 3) for x in triangle.sides]
    angles = [round(math.degrees(x), 3) for x in triangle.angles]
    print("Sides: " + str(sides))
    print("Angles: " + str(angles))
    print("Perimeter: " + str(round(triangle.perimeter, 3)))
    print("Area: " + str(round(triangle.area, 3)))


def solve(sides, angles):
    """Main solving routine"""
    angles = [math.radians(x) if x else None for x in angles]
    solver = TriangleSolver(ensure_size(sides, None, 3), ensure_size(angles, None, 3))

    solver.solve()
    return Triangle(
        sides=solver.sides,
        angles=solver.angles,
        altitudes=solver.altitudes,
        medians=solver.medians,
        perimeter=solver.perimeter,
        area=solver.area,
    )
