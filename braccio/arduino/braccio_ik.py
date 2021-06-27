from collections import namedtuple
from dataclasses import dataclass
from math import acos, cos, degrees, pi, radians, atan2, sin, sqrt
from typing import Optional

from routines.models import Position

# This code was adapted from https://github.com/cgxeiji/CGx-InverseK/


@dataclass
class Link:
    length: int  # in millimeters
    angle_min: float  # in radians
    angle_max: float

    def in_range(self, angle):
        return self.angle_min <= angle <= self.angle_max


BASE = Link(
    0,  # this actually indicated the heigth of the base
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

    calculated_cos = (
        pow(adjacent1, 2) + pow(adjacent2, 2) - pow(opposite, 2)) / delta
    if calculated_cos > 1 or calculated_cos < -1:
        return None

    angle = acos(calculated_cos)
    return angle


def _solve_xy_angle(x, y, attack_angle):

    # find coordinates of wrist
    x_wrist = x + HAND.length * cos(attack_angle)
    y_wrist = y + HAND.length * sin(attack_angle)

    # get polar coordinates
    alpha = atan2(y_wrist, x_wrist)
    r = distance(ORIGIN, Point(x_wrist, y_wrist))

    # inner angle of shoulder
    beta = cos_rule(FOREARM.length, r, UPPERARM.length)
    if beta is None:
        return None

    # inner angle of elbow
    gamma = cos_rule(r, UPPERARM.length, FOREARM.length)
    if gamma is None:
        return None

    # solve angles
    shoulder = alpha - beta
    elbow = pi - gamma
    wrist = attack_angle - shoulder - elbow

    def all_in_range():
        return UPPERARM.in_range(
            shoulder) and FOREARM.in_range(elbow) and HAND.in_range(wrist)

    if not all_in_range():
        # try second soulution
        shoulder += 2 * beta
        elbow = -elbow
        wrist = attack_angle - shoulder - elbow

        if not all_in_range():
            return None

    return shoulder, elbow, wrist


def _solve_xy(x, y):
    # test every angle to find a valid solution
    for i in range(0, 360):
        attack_angle = radians(i)
        result = _solve_xy_angle(x, y, attack_angle)
        if result is not None:
            return result

    return None


def _solve(x: int, y: int, z: int, attack_angle: Optional[float] = None):

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
        res = _solve_xy(r, z - BASE.length)
    else:
        res = _solve_xy_angle(
            r, z - BASE.length, attack_angle)

    if res is None:
        return None

    shoulder, elbow, wrist = res
    return base, shoulder, elbow, wrist


def solve_ik(position: Position, attack_angle: Optional[int] = None):
    # prepare inputs
    x, y, z = position
    attack_angle = radians(attack_angle) if attack_angle is not None else None

    result = _solve(x, y, z, attack_angle)
    if result is None:
        return None

    base, shoulder, elbow, wrist = result
    return int(degrees(base)), int(degrees(shoulder)), int(degrees(elbow)), int(degrees(wrist))
