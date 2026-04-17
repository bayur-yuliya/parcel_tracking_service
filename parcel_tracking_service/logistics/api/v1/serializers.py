from rest_framework import serializers

from logistics.models import ParcelStatusHistory, Parcel


class ParcelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            "sender",
            "recipient",
            "weight",
            "declared_value",
            "origin_office",
            "destination_office",
        ]


class ParcelStatusHistorySerializer(serializers.ModelSerializer):
    origin_office = serializers.PrimaryKeyRelatedField(read_only=True)
    destination_office = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ParcelStatusHistory
        fields = ["status", "office", "comment", "created_at"]


class ParcelSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    recipient = serializers.StringRelatedField()
    origin_office = serializers.PrimaryKeyRelatedField(read_only=True)
    destination_office = serializers.PrimaryKeyRelatedField(read_only=True)
    status_history = ParcelStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Parcel
        fields = [
            "tracking_number",
            "sender",
            "recipient",
            "weight",
            "declared_value",
            "status",
            "origin_office",
            "destination_office",
            "created_at",
            "status_history",
        ]


class UpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Parcel._meta.get_field("status").choices)
    office_id = serializers.UUIDField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
