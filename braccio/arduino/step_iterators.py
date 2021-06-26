from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Iterable
from routines.models import Routine, Position


@dataclass
class Step:
    speed: int
    delay: int
    attack_angle: int
    gripper: int
    gripper_rot: int
    position: Position
    wait_for_position: bool


class StepIterator(ABC, Iterable[Step]):

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class RoutineStepIterator(StepIterator):

    def __init__(self, routine: Routine):
        self.routine = routine

    @property
    def name(self):
        return self.routine.name

    def __iter__(self):
        for routine_step in self.routine.steps.all():
            yield Step(
                speed=routine_step.speed,
                delay=routine_step.delay,
                attack_angle=routine_step.attack_angle,
                gripper=routine_step.gripper,
                gripper_rot=routine_step.gripper_rot,
                position=routine_step.position,
                wait_for_position=True,
            )


class ContinuousStepIterator(StepIterator):

    name = 'remote_control'

    def __init__(self):
        # FIXME: set sensible defaults
        self.speed = 30
        self.attack_angle = None
        self.gripper = 10
        self.gripper_rot = 45
        self.position = Position(0, 0, 0)
        self._stop = False

    def stop(self):
        self._stop = True

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration

        return Step(
            delay=100,
            wait_for_position=False,
            speed=self.speed,
            attack_angle=self.attack_angle,
            gripper=self.gripper,
            gripper_rot=self.gripper_rot,
            position=self.position,
        )
