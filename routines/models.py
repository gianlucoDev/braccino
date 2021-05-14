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
    m1 = models.IntegerField()
    m2 = models.IntegerField()
    m3 = models.IntegerField()
    m4 = models.IntegerField()
    m5 = models.IntegerField()
    m6 = models.IntegerField()

    @property
    def position(self) -> Position:
        return Position(
            base=self.m1,
            shoulder=self.m2,
            elbow=self.m3,
            wrist_ver=self.m4,
            wrist_rot=self.m5,
            gripper=self.m6,
        )

    @position.setter
    def position(self, position: Position):
        self.m1 = position.base
        self.m2 = position.shoulder
        self.m3 = position.elbow
        self.m4 = position.wrist_ver
        self.m5 = position.wrist_rot
        self.m6 = position.gripper

    class Meta:
        ordering = ['order']
