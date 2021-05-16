from routines.models import Routine, Position
from braccio.arduino.braccio import BraccioStep


def routine_step_iterator(routine: Routine):
    for step in routine.steps.all():
        yield BraccioStep(
            position=step.position,
            speed=step.speed,
            delay=step.delay,
            wait_for_position=True,
        )


class ContinuousStepIterator:

    def __init__(self):
        self._position = Position()
        self._speed = 30
        self._stop = False

    def position(self, position: Position):
        self._position = position

    def speed(self, speed):
        # TODO: use this method
        self._speed = speed

    def stop(self):
        self._stop = True

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration

        return BraccioStep(
            position=self._position,
            speed=self._speed,
            delay=100,
            wait_for_position=False,
        )
