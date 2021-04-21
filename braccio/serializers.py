from rest_framework import serializers
from .models import Braccio, Routine, Step


class BraccioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Braccio
        fields = ['id', 'name', 'serial']


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['delay', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6']


class RoutineSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True)

    class Meta:
        model = Routine
        fields = ['id', 'name', 'steps']

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        routine = Routine.objects.create(**validated_data)
        for i, step_data in enumerate(steps_data):
            Step.objects.create(routine=routine, order=i, **step_data)
        return routine
