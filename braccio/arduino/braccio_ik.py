from collections import namedtuple
from dataclasses import dataclass
from math import acos, degrees, pi, radians, atan2, sqrt

from routines.models import Position


@dataclass
class Link:
    length: int  # in millimeters
    angle_min: float  # in radians
    angle_max: float

    def in_range(self, angle):
        return self.angle_min <= angle <= self.angle_max


BASE = Link(
    0,
    radians(0),
    radians(180))

UPPERARM = Link(
    200,
    radians(15),
    radians(165))

FOREARM = Link(
    200,
    radians(0),
    radians(180))

HAND = Link(
    270,
    radians(0),
    radians(180))


Point = namedtuple('Point', ('x', 'y'))
ORIGIN = Point(0, 0)


def distance(p1: Point, p2: Point):
    x1, y1 = p1
    x2, y2 = p2
    return sqrt(pow(x1-x2, 2)+pow(y1-y2, 2))


def cos_rule(opposite, adjacent1, adjacent2):
    delta = 2 * adjacent1 * adjacent2

    if delta == 0:
        return None

    cos = (pow(adjacent1, 2) + pow(adjacent2, 2) - pow(opposite, 2)) / delta
    if cos > 1 or cos < -1:
        return None

    angle = acos(cos)
    return angle


def solve_xy_angle(x, y, attack_angle):
    raise NotImplementedError


def solve_xy(x, y):
    # test every angle to find a valid solution
    for i in range(0, 360):
        attack_angle = radians(i)
        result = solve_xy_angle(x, y, attack_angle)
        if result is not None:
            return result

    return None


def solve_ik(position: Position, attack_angle: int):
    """
    Given a position and an attack angle, calculate the inverse kinematics for the Arduino Braccio.
    Returns the calculated ik, or `None` if no solution is found.

    Used https://github.com/cgxeiji/CGx-InverseK as reference.
    """

    # prepare inputs
    x, y, z = position
    attack_angle = radians(attack_angle)

    # calculate base angle
    r = distance(ORIGIN, Point(x, y))
    base = atan2(y, x)

    if not BASE.in_range(base):
        base += pi if base < 0 else -pi
        r = -r

        if attack_angle is not None:
            attack_angle = pi - attack_angle

    # calculate other angles
    if attack_angle is None:
        res = solve_xy(r, z - BASE.length)
    else:
        res = solve_xy_angle(
            r, z - BASE.length, attack_angle)

    if res is None:
        return None

    # convert to degrees and return
    shoulder, elbow, wrist = res
    return degrees(base), degrees(shoulder), degrees(elbow), degrees(wrist)
