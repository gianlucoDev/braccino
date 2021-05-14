import threading
import time

from routines.models import Routine
from .braccio import Braccio, BraccioAction


class BraccioRoutineAction(BraccioAction):
    def __init__(self, braccio: Braccio, routine: Routine):
        self._name = routine.name
        self.braccio = braccio
        self.routine = routine
        self.current_step = 0
        self.thread = threading.Thread(target=self._run)

    def _run(self):
        for step in self.routine.steps.all():
            pos = (step.m1, step.m2, step.m3, step.m4, step.m5, step.m6)

            # set target position and speed
            self.braccio.set_target_position(*pos)
            self.braccio.set_speed(step.speed)

            # wait for the braccio to reach position
            self.braccio.wait_for_position(pos)

            # wait specified delay
            time.sleep(step.delay / 1000)

    @property
    def name(self):
        return self._name

    def start(self):
        self.thread.start()

    def is_running(self):
        return self.thread.is_alive()
