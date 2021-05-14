from rest_framework import serializers
from .models import Position, Routine, Step


class PositionSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    def to_representation(self, instance: Position):
        json = {
            "base": instance.base,
            "shoulder": instance.shoulder,
            "elbow": instance.elbow,
            "wrist_ver": instance.wrist_ver,
            "wrist_rot": instance.wrist_rot,
            "gripper": instance.gripper,
        }
        return json

    def to_internal_value(self, data) -> Position:
        position = Position(
            base=data["base"],
            shoulder=data["shoulder"],
            elbow=data["elbow"],
            wrist_ver=data["wrist_ver"],
            wrist_rot=data["wrist_rot"],
            gripper=data["gripper"],
        )
        return position


class StepSerializer(serializers.ModelSerializer):
    position = PositionSerializer()

    class Meta:
        model = Step
        fields = ['delay', 'speed', 'position']


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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        steps_data = validated_data.get('steps')
        if steps_data is not None:
            instance.steps.all().delete()
            for i, step_data in enumerate(steps_data):
                Step.objects.create(routine=instance, order=i, **step_data)

        instance.save()
        return instance
