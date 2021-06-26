import threading
import time
from dataclasses import dataclass
from .braccio_ik import solve_ik

from .arduino import Arduino
from .step_iterators import StepIterator

# django -> arduino
SETPOS_ID = 0x01
GETPOS_ID = 0x02
SETSPEED_ID = 0x03

# django <- arduino
GETPOS_REPLY_ID = 0x02


@dataclass
class Angles:
    base: int = 90
    shoulder: int = 45
    elbow: int = 180
    wrist_ver: int = 180
    wrist_rot: int = 90
    gripper: int = 10


class Braccio(Arduino):

    def __init__(self, name, serial_number, serial_path):
        self.thread = None
        self.running = None
        super().__init__(name, serial_number, serial_path)

    def set_target_angles(self, angles: Angles):
        self._write_packet([SETPOS_ID,
                            angles.base,
                            angles.shoulder,
                            angles.elbow,
                            angles.wrist_ver,
                            angles.wrist_rot,
                            angles.gripper,
                            ])

    def get_current_angles(self) -> Angles:
        self._write_packet([GETPOS_ID])
        data = self._read_packet(timeout=1)

        # ignore fist byte because it's packet ID
        return Angles(
            base=data[1],
            shoulder=data[2],
            elbow=data[3],
            wrist_ver=data[4],
            wrist_rot=data[5],
            gripper=data[6],
        )

    def wait_for_position(self, expected):
        current = self.get_current_angles()
        while current != expected:
            current = self.get_current_angles()

    def set_speed(self, speed):
        self._write_packet([SETSPEED_ID, speed])

    def _run_thread(self, steps: StepIterator):
        self.running = steps

        for step in steps:
            # solve ik and create Angles()
            base, shoulder, elbow, wrist = solve_ik(
                step.position, step.attack_angle)
            angles = Angles(base, shoulder, elbow, wrist,
                            step.gripper_rotation, step.gripper)

            # set angles and speed
            self.set_target_angles(angles)
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
