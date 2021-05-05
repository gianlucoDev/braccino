from .arduino import Arduino


class Braccio(Arduino):

    def set_target_position(self, m1, m2, m3, m4, m5, m6):
        self._write_packet([0x01, m1, m2, m3, m4, m5, m6])

    def get_current_position(self):
        self._write_packet([0x02])
        data = self._read_packet()

        # ignore fist byte because it's packet ID
        # return bytes 1-6 as m1, m2, m3, m4, m5, m6
        return tuple(data[1:7])
