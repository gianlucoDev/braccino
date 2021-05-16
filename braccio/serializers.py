from rest_framework import serializers


class ConnectionStatusSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    def to_representation(self, instance):
        return {"ok": instance.ok, "code": instance.name}


class BraccioSerializer(serializers.Serializer):
    # pylint: disable=abstract-method

    name = serializers.CharField(max_length=200)
    serial_number = serializers.CharField(max_length=200)
    serial_path = serializers.CharField(max_length=200)
    connection_status = ConnectionStatusSerializer()
    is_busy = serializers.BooleanField()
