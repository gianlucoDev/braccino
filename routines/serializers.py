from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Position, Routine, Step

JOINTS = {
    'base': (0, 180),
    'shoulder': (15, 165),
    'elbow': (0, 180),
    'wrist_ver': (0, 180),
    'wrist_rot': (0, 180),
    'gripper': (10, 73),
}


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

    def validate(self, attrs: Position):
        invalid = {}

        def check_min_max(value, name):
            min_value, max_value = JOINTS[name]
            if value < min_value or value > max_value:
                invalid[name] = f"Ensure this value is between {min_value} and {max_value}."

        check_min_max(attrs.base, 'base')
        check_min_max(attrs.shoulder, 'shoulder')
        check_min_max(attrs.elbow, 'elbow')
        check_min_max(attrs.wrist_ver, 'wrist_ver')
        check_min_max(attrs.wrist_rot, 'wrist_rot')
        check_min_max(attrs.gripper, 'gripper')

        if invalid:
            raise ValidationError(invalid)

        return attrs


class StepSerializer(serializers.ModelSerializer):
    delay = serializers.IntegerField(min_value=0)
    speed = serializers.IntegerField(min_value=10, max_value=30)
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
