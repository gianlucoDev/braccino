from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Iterable
from routines.models import Routine, Position


@dataclass
class Step:
    position: Position
    speed: int
    delay: int
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
                position=routine_step.position,
                speed=routine_step.speed,
                delay=routine_step.delay,
                wait_for_position=True,
            )


class ContinuousStepIterator(StepIterator):

    name = 'remote_control'

    def __init__(self):
        self._position = Position()
        self._speed = 30
        self._stop = False

    def position(self, position: Position):
        self._position = position

    def speed(self, speed):
        self._speed = speed

    def stop(self):
        self._stop = True

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration

        return Step(
            position=self._position,
            speed=self._speed,
            delay=100,
            wait_for_position=False,
        )
