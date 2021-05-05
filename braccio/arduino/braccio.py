import time
import threading

from routines.models import Routine
from .arduino import Arduino


class Braccio(Arduino):

    def __init__(self, name, serial_number, serial_path):
        self.routine = None
        self.current_step = None
        super().__init__(name, serial_number, serial_path)

    def _set_target_position(self, m1, m2, m3, m4, m5, m6):
        self._write_packet([0x01, m1, m2, m3, m4, m5, m6])

    def _get_current_position(self):
        self._write_packet([0x02])
        data = self._read_packet()

        # ignore fist byte because it's packet ID
        # return bytes 1-6 as m1, m2, m3, m4, m5, m6
        return tuple(data[1:7])

    def _wait_for_position(self, expected):
        current = self._get_current_position()
        while current != expected:
            current = self._get_current_position()
            time.sleep(500 / 1000)

    def _run(self):
        for step in self.routine.steps.all():
            pos = (step.m1, step.m2, step.m3, step.m4, step.m5, step.m6)

            self.set_target_position(*pos)
            self._wait_for_position(pos)
            time.sleep(step.delay / 1000)

        self.routine = None
        self.current_step = None

    def run(self, routine: Routine):
        if self.routine is not None:
            raise ValueError("Already running")

        self.routine = routine
        self.current_step = 0
        thread = threading.Thread(target=self._run)
        thread.start()
