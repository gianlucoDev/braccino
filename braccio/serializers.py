from rest_framework import serializers
from .models import Routine, Step


class BraccioStatusSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    def to_representation(self, instance):
        return {"ok": instance.ok, "code": instance.name}


class BraccioSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    name = serializers.CharField(max_length=200)
    serial_path = serializers.CharField(max_length=200)
    status = BraccioStatusSerializer()


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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        steps_data = validated_data.get('steps')
        if steps_data:
            instance.steps.all().delete()
            for i, step_data in enumerate(steps_data):
                Step.objects.create(routine=instance, order=i, **step_data)

        instance.save()
        return instance
