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


class RepeatingStepIterator(StepIterator):

    name = 'remote_control'

    def __init__(self):
        self._step = Step(
            speed=20,
            attack_angle=None,
            gripper=50,
            gripper_rot=0,
            position=Position(50, 0, 200),
            delay=100,
            wait_for_position=False,
        )
        self._stop = False

    def update(self, data):
        if self._stop:
            raise ValueError(
                "Attempted to update the value after the iterator has already stopped")

        self._step = Step(
            speed=data["speed"],
            attack_angle=data["attack_angle"],
            gripper=data["gripper"],
            gripper_rot=data["gripper_rot"],
            position=data["position"],
            delay=0,
            wait_for_position=False,
        )

    def stop(self):
        self._stop = True

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration
        return self._step
