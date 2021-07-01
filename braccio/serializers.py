from rest_framework import serializers
from routines.serializers import PositionSerializer


class ConnectionStatusSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    def to_representation(self, instance):
        return {"ok": instance.ok, "code": instance.name}


class BraccioRunningSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    name = serializers.CharField(max_length=200)


class BraccioSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    name = serializers.CharField(max_length=200)
    serial_number = serializers.CharField(max_length=200)
    serial_path = serializers.CharField(max_length=200)
    connection_status = ConnectionStatusSerializer()
    running = BraccioRunningSerializer()


class BraccioPositionUpdateCommandSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    speed = serializers.IntegerField(min_value=10, max_value=30)
    attack_angle = serializers.IntegerField(
        min_value=0, max_value=360, required=False, allow_null=True)
    gripper = serializers.IntegerField(min_value=10, max_value=73)
    gripper_rot = serializers.IntegerField(min_value=0, max_value=180)
    position = PositionSerializer()
