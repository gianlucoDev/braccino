import threading
import time
import struct
import logging
from dataclasses import dataclass
from django.conf import settings

from .arduino import Arduino
from .step_iterators import StepIterator
from .ik import braccio_ik

logger = logging.getLogger(__name__)

# django -> arduino
SETPOS_ID = 0x01
POS_QUERY_ID = 0x02
SETSPEED_ID = 0x03

# django <- arduino
HELLO_ID = 0x00
SETPOS_REPLY_ID = 0x01
POS_QUERY_REPLY_ID = 0x02


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
        send_data = struct.pack(
            '<BBBBBBB',
            SETPOS_ID,
            angles.base,
            angles.shoulder,
            angles.elbow,
            angles.wrist_ver,
            angles.wrist_rot,
            angles.gripper,
        )
        self._write_packet(send_data)

    def is_on_position(self) -> bool:
        send_data = struct.pack('<B', POS_QUERY_ID)
        self._write_packet(send_data)

        recv_data = self._read_packet(timeout=1)
        _id, ok = struct.unpack('<B?', recv_data)
        return ok

    def wait_for_position_reached(self):
        # FIXME: this is ugly.
        # I should make it so the the Arduino sends a message when the position has been reached
        while not self.is_on_position():
            pass

    def set_speed(self, speed):
        data = struct.pack('<BB', SETSPEED_ID, speed)
        self._write_packet(data)

    def _run_thread(self, steps: StepIterator):
        self.running = steps

        for step in steps:
            ik_angles = braccio_ik(step.position, step.attack_angle)
            if ik_angles is None:
                logger.warning('position unreachable %s', step.position)
                continue

            angles = Angles(
                base=ik_angles.base,
                shoulder=ik_angles.shoulder,
                elbow=ik_angles.elbow,
                wrist_ver=ik_angles.wrist_ver,
                wrist_rot=step.gripper_rot,
                gripper=step.gripper,
            )

            if settings.BRACCIO_SIMULATION_MODE:
                # if we are in simulation mode, do not actually send commands to the braccio
                continue

            self.set_speed(step.speed)
            self.set_target_angles(angles)

            if step.wait_for_position:
                self.wait_for_position_reached()

            # wait specified delay
            time.sleep(step.delay / 1000)

        self.running = None

    def run(self, steps: StepIterator):
        self.thread = threading.Thread(
            target=self._run_thread, args=(steps,))
        self.thread.start()

    def is_busy(self):
        return self.running is not None
