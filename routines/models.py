from collections import namedtuple
from django.db import models


class Routine(models.Model):
    name = models.CharField(max_length=50)


Position = namedtuple('Position', ('x', 'y', 'z'))

class Step(models.Model):
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()

    delay = models.IntegerField()
    speed = models.IntegerField()

    # position
    _x = models.IntegerField()
    _y = models.IntegerField()
    _z = models.IntegerField()

    @property
    def position(self) -> Position:
        return Position(self._x, self._y, self._z)

    @position.setter
    def position(self, position: Position):
        self._x = position.x
        self._y = position.y
        self._z = position.z

    class Meta:
        ordering = ['order']
