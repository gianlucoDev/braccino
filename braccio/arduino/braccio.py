from routines.models import Position
import time
from abc import ABC, abstractmethod

from .arduino import Arduino


# django -> arduino
SETPOS_ID = 0x01
GETPOS_ID = 0x02
SETSPEED_ID = 0x03

# django <- arduino
GETPOS_REPLY_ID = 0x02


class BraccioController(ABC):

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def is_running(self) -> bool:
        raise NotImplementedError


class Braccio(Arduino):

    def __init__(self, name, serial_number, serial_path):
        self.current_action = None
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

    def run_action(self, action):
        if self.is_busy():
            raise ValueError('Braccio busy')

        self.current_action = action
        self.current_action.start()

    def is_busy(self):
        return self.current_action is not None and self.current_action.is_running()
