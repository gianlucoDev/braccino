import threading
import time
import struct
from dataclasses import dataclass
from math import degrees
from django.conf import settings
from ikpy.chain import Chain

from .arduino import Arduino
from .step_iterators import StepIterator


# Braccio kinematic chain.
# Links:
#   0: origin link inserted by ikpy, unused
#   1: base
#   2: shoulder
#   3: elbow
#   4: wrist_ver
#   5: wrist_rot
#   6: gripper_base, unused
#   7: gripper_fix, unused
braccio_chain = Chain.from_urdf_file(
    settings.BASE_DIR.joinpath('./braccio-urdf/urdf/braccio.urdf'),
    active_links_mask=[False, True, True, True, True, False, False, False],
    name='braccio')


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
            # scale from millimiters to meters
            position = [step.position.x / 1000,
                        step.position.y / 1000,
                        step.position.z / 1000]

            # TODO: take into account attack_angle
            ik = braccio_chain.inverse_kinematics(
                target_position=position)

            # convert ik solution to braccio angles
            ik_degrees = [int(degrees(rad_angle)) for rad_angle in ik]
            angles = Angles(
                base=ik_degrees[1],
                shoulder=ik_degrees[2],
                elbow=ik_degrees[3],
                wrist_ver=ik_degrees[4],
                wrist_rot=step.gripper_rot,
                gripper=step.gripper,
            )

            # send data to braccio
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
