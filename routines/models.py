from django.db import models


class Routine(models.Model):
    name = models.CharField(max_length=50)


class Step(models.Model):
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name='steps')
    order = models.IntegerField()

    delay = models.IntegerField()
    m1 = models.IntegerField()
    m2 = models.IntegerField()
    m3 = models.IntegerField()
    m4 = models.IntegerField()
    m5 = models.IntegerField()
    m6 = models.IntegerField()

    class Meta:
        ordering = ['order']
