from typing import Optional, Tuple
from collections import namedtuple
from dataclasses import dataclass
from django.conf import settings

from numpy import arccos, arctan2, cos, deg2rad, pi, rad2deg, sin, sqrt
import matplotlib.pyplot as plt

from routines.models import Position


@dataclass
class Link:
    length: int  # in millimeters
    angle_min: float  # in radians
    angle_max: float

    def in_range(self, angle):
        return self.angle_min <= angle <= self.angle_max


BASE = Link(
    0,  # this actually indicates the heigth of the base
    deg2rad(0),
    deg2rad(180))

UPPERARM = Link(
    125,
    deg2rad(15),
    deg2rad(165))

FOREARM = Link(
    125,
    deg2rad(0),
    deg2rad(180))

HAND = Link(
    195,
    deg2rad(0),
    deg2rad(180))

IkAngles = namedtuple('IkAngles',
                      field_names=('base', 'shoulder', 'elbow', 'wrist_ver'),
                      defaults=(0, 45, 180, 180))


def invert_angle(angle):
    # invert the angle but keeping it in the 0 - 2pi range
    return (angle + pi) % (2 * pi)


def find_base_angle(pos: Position):
    # convert from cartesian coordinates to polar coordinates
    r = sqrt(pos.x ** 2 + pos.y ** 2)
    phi = arctan2(pos.y, pos.x)

    # if the angle is reachable, return polar coordinates
    if BASE.in_range(phi):
        return False, r, phi

    # If the angles is not reachable, try inverting it.
    # If we invert the angle then we should also invert the length, this way the
    # polar coordinates will indicate the same point: (r, phi) = (-r, -phi)
    inverted_phi = invert_angle(phi)
    if BASE.in_range(inverted_phi):
        return True, -r, inverted_phi

    # the angle is not reachable
    return None


def cos_rule(opposite: float, adjacent1: float, adjacent2: float):
    delta = 2 * adjacent1 * adjacent2
    if delta == 0:
        return None

    calculated_cos = (adjacent1 ** 2 + adjacent2 ** 2 - opposite ** 2) / delta
    if calculated_cos > 1 or calculated_cos < -1:
        return None

    angle = arccos(calculated_cos)
    return angle


def solve_triangle(a: float, b: float, c: float):
    alpha = cos_rule(a, b, c)
    beta = cos_rule(b, c, a)
    gamma = cos_rule(c, a, b)

    if alpha is None or beta is None or gamma is None:
        return None
    else:
        return alpha, beta, gamma


def find_arm_angles(x: float, y: float, attack_angle: float):
    c_x = x - HAND.length * cos(attack_angle)
    c_y = y - HAND.length * sin(attack_angle)

    c_length = sqrt(c_x ** 2 + c_y ** 2)
    phi = arctan2(c_y, c_x)

    solution = solve_triangle(UPPERARM.length, FOREARM.length, c_length)
    if solution is None:
        return None

    # alpha -> (opposite to UPPERARM)
    # beta -> shoulder (opposite to FOREARM)
    # gamma -> elbow (opposite to c side)
    _alpha, beta, gamma = solution

    shoulder_angle = phi + beta
    elbow_angle = gamma - pi/2
    wrist_ver_angle = invert_angle(attack_angle - shoulder_angle - elbow_angle)

    if UPPERARM.in_range(shoulder_angle) \
            and FOREARM.in_range(elbow_angle) \
            and HAND.in_range(wrist_ver_angle):
        return attack_angle, shoulder_angle, elbow_angle, wrist_ver_angle

    shoulder_angle = phi - beta
    elbow_angle = pi - (gamma - pi/2)
    wrist_ver_angle = invert_angle(attack_angle - shoulder_angle - elbow_angle)

    if UPPERARM.in_range(shoulder_angle) \
            and FOREARM.in_range(elbow_angle) \
            and HAND.in_range(wrist_ver_angle):
        return attack_angle, shoulder_angle, elbow_angle, wrist_ver_angle

    return None


def find_arm_angles_without_attack_angle(x: float, y: float):
    # just try every possible angle, one will probably work ¯\_(ツ)_/¯
    for a in range(0, 360):
        a = deg2rad(a)
        solution = find_arm_angles(x, y, a)

        if solution is not None:
            return solution

    return None


def calculate_ik(pos: Position, attack_angle: Optional[float] = None):
    result = find_base_angle(pos)
    if result is None:
        return None

    inverted, r, base_angle = result
    if inverted and attack_angle is not None:
        attack_angle = pi - attack_angle

    if attack_angle is not None:
        found_angles = find_arm_angles(
            r, pos.z - BASE.length, attack_angle)
    else:
        found_angles = find_arm_angles_without_attack_angle(
            r, pos.z - BASE.length)

    if found_angles is None:
        return None

    found_attack_angle, shoulder_angle, elbow_angle, wrist_ver_angle = found_angles
    if settings.BRACCIO_SIMULATION_MODE:
        display_plot(found_attack_angle, shoulder_angle, elbow_angle, wrist_ver_angle,
                    target=(r, pos.z - BASE.length))

    return base_angle, shoulder_angle, elbow_angle, wrist_ver_angle


def braccio_ik(pos: Position, attack_angle: Optional[int] = None) -> Optional[IkAngles]:
    # convert to radians
    a = None if attack_angle is None else deg2rad(attack_angle)

    # do calculations
    solution = calculate_ik(pos, attack_angle=a)
    if solution is None:
        return None

    # convert back to degrees
    base, shoulder, elbow, wrist_ver = solution
    return IkAngles(
        base=int(rad2deg(base)),
        shoulder=int(rad2deg(shoulder)),
        elbow=int(rad2deg(elbow)),
        wrist_ver=int(rad2deg(wrist_ver))
    )


# plot stuff

Point = namedtuple('Point', field_names=('x', 'y'))


def display_plot(attack_angle, shoulder, elbow, wrist_ver, target: Tuple[float, float]):
    p0 = Point(0, 0)

    p1 = Point(
        p0.x + UPPERARM.length * cos(shoulder),
        p0.y + UPPERARM.length * sin(shoulder)
    )

    p2 = Point(
        p1.x + FOREARM.length * cos(shoulder + (elbow - pi/2)),
        p1.y + FOREARM.length * sin(shoulder + (elbow - pi/2))
    )

    p3 = Point(
        p2.x + HAND.length *
        cos(shoulder + (elbow - pi/2) + (wrist_ver - pi/2)),
        p2.y + HAND.length *
        sin(shoulder + (elbow - pi/2) + (wrist_ver - pi/2))
    )

    braccio = [p0, p1, p2, p3]

    x_values = [p.x for p in braccio]
    y_values = [p.y for p in braccio]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # draw braccio
    ax.plot(x_values, y_values)
    ax.plot(x_values, y_values, 'bo')

    # draw target pos
    ax.plot([target[0]], [target[1]], 'rx')

    # add text with attack angle
    plt.figtext(0.70, 0.90, f'Attack angle: {rad2deg(attack_angle)}°')

    ax.axhline(0, color='black')
    ax.axvline(0, color='black')
    ax.set_xlim(-500, 500)
    ax.set_ylim(-200, 500)

    plt.show()
