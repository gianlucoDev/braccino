from dataclasses import dataclass
from django.db import models


class Routine(models.Model):
    name = models.CharField(max_length=50)


@dataclass
class Position:
    base: int
    shoulder: int
    elbow: int
    wrist_ver: int
    wrist_rot: int
    gripper: int


class Step(models.Model):
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()

    delay = models.IntegerField()
    speed = models.IntegerField()

    # position
    _m1 = models.IntegerField()
    _m2 = models.IntegerField()
    _m3 = models.IntegerField()
    _m4 = models.IntegerField()
    _m5 = models.IntegerField()
    _m6 = models.IntegerField()

    @property
    def position(self) -> Position:
        return Position(
            base=self._m1,
            shoulder=self._m2,
            elbow=self._m3,
            wrist_ver=self._m4,
            wrist_rot=self._m5,
            gripper=self._m6,
        )

    @position.setter
    def position(self, position: Position):
        self._m1 = position.base
        self._m2 = position.shoulder
        self._m3 = position.elbow
        self._m4 = position.wrist_ver
        self._m5 = position.wrist_rot
        self._m6 = position.gripper

    class Meta:
        ordering = ['order']
