from rest_framework import serializers
from .models import Position, Routine, Step


class PositionSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    def to_representation(self, instance: Position):
        json = {
            "x": instance.x,
            "y": instance.y,
            "z": instance.z,
        }
        return json

    def to_internal_value(self, data) -> Position:
        position = Position(
            data["x"],
            data["y"],
            data["z"],
        )
        return position


class StepSerializer(serializers.ModelSerializer):
    delay = serializers.IntegerField(min_value=0)
    speed = serializers.IntegerField(min_value=10, max_value=30)

    attack_angle = serializers.IntegerField(
        min_value=0, max_value=360, required=False, allow_null=True)
    gripper = serializers.IntegerField(min_value=10, max_value=73)
    gripper_rot = serializers.IntegerField(min_value=0, max_value=180)

    position = PositionSerializer()

    class Meta:
        model = Step
        fields = ['delay', 'speed', 'attack_angle',
                  'gripper', 'gripper_rot', 'position']


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
