from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import (
    ParcelSerializer,
    ParcelCreateSerializer,
    UpdateStatusSerializer,
)
from ...models import Parcel, PostOffice, Status
from ...services.parcel_service import update_status
from ...services.services import StandardPagination


class ParcelListCreateView(generics.ListCreateAPIView):
    queryset = Parcel.objects.select_related(
        "sender",
        "recipient",
        "origin_office",
        "destination_office",
        "current_office",
    )
    serializer_class = ParcelSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "origin_office"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ParcelCreateSerializer
        return ParcelSerializer


class ParcelDetailView(APIView):
    def get(self, request, tracking_number):
        parcel = get_object_or_404(Parcel, tracking_number=tracking_number)
        serializer = ParcelSerializer(parcel)
        return Response(serializer.data)


class ParcelUpdateStatusView(APIView):
    def post(self, request, tracking_number):
        parcel = get_object_or_404(Parcel, tracking_number=tracking_number)

        serializer = UpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        office = None
        office_id = serializer.validated_data.get("office_id")

        if office_id:
            office = get_object_or_404(PostOffice, id=office_id)

        updated_parcel = update_status(
            parcel_id=parcel.id,
            new_status=serializer.validated_data["status"],
            office=office,
            comment=serializer.validated_data.get("comment", ""),
        )

        return Response({"status": updated_parcel.status})


class OfficeParcelsView(APIView):
    pagination_class = StandardPagination

    def get(self, request, office_id):
        parcels = Parcel.objects.filter(
            status=Status.ARRIVED,
            current_office_id=office_id,
            destination_office_id=office_id,
        )

        serializer = ParcelSerializer(parcels, many=True)
        return Response(serializer.data)
