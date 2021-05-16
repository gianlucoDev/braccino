import threading
import time

from routines.models import Position
from .arduino import Arduino
from .step_iterators import StepIterator

# django -> arduino
SETPOS_ID = 0x01
GETPOS_ID = 0x02
SETSPEED_ID = 0x03

# django <- arduino
GETPOS_REPLY_ID = 0x02


class Braccio(Arduino):

    def __init__(self, name, serial_number, serial_path):
        self.thread = None
        self.running = None
        super().__init__(name, serial_number, serial_path)

    def set_target_position(self, position: Position):
        self._write_packet([SETPOS_ID,
                            position.base,
                            position.shoulder,
                            position.elbow,
                            position.wrist_ver,
                            position.wrist_rot,
                            position.gripper,
                            ])

    def get_current_position(self):
        self._write_packet([GETPOS_ID])
        data = self._read_packet(timeout=1)

        # ignore fist byte because it's packet ID
        return Position(
            base=data[1],
            shoulder=data[2],
            elbow=data[3],
            wrist_ver=data[4],
            wrist_rot=data[5],
            gripper=data[6],
        )

    def wait_for_position(self, expected):
        current = self.get_current_position()
        while current != expected:
            current = self.get_current_position()
            time.sleep(0.1)

    def set_speed(self, speed):
        self._write_packet([SETSPEED_ID, speed])

    def _run_thread(self, steps: StepIterator):
        self.running = steps

        for step in steps:
            # set target position and speed
            self.set_target_position(step.position)
            self.set_speed(step.speed)

            # wait for the braccio to reach position
            if step.wait_for_position:
                self.wait_for_position(step.position)

            # wait specified delay
            time.sleep(step.delay / 1000)

        self.running = None

    def run(self, steps: StepIterator):
        self.thread = threading.Thread(
            target=self._run_thread, args=(steps,))
        self.thread.start()

    def is_busy(self):
        return self.running is not None
