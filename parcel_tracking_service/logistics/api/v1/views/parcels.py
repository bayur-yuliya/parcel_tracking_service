import logging
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from logistics.api.permissions import IsEmployee
from logistics.api.v1.filters import ParcelFilter
from logistics.api.v1.serializers import (
    ParcelSerializer,
    ParcelCreateSerializer,
    UpdateStatusSerializer,
)
from logistics.models import Parcel, PostOffice, Status
from logistics.services.parcel_service import update_status
from logistics.services.services import StandardPagination

logger = logging.getLogger(__name__)


class ParcelListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
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
    filterset_class = ParcelFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parcel = serializer.save()

        return Response(
            {"tracking_number": parcel.tracking_number}, status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ParcelCreateSerializer
        return ParcelSerializer


class ParcelDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Parcel.objects.select_related(
        "sender", "recipient", "current_status"
    ).prefetch_related("status_history")
    lookup_field = "tracking_number"
    serializer_class = ParcelSerializer


class ParcelUpdateStatusView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = UpdateStatusSerializer

    def create(self, request, *args, **kwargs):
        tracking_number = self.kwargs.get("tracking_number")
        get_object_or_404(Parcel, tracking_number=tracking_number)

        logger.info(
            f"POST request to update status for {tracking_number} by user {request.user}"
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        office_id = serializer.validated_data.get("office_id")
        office = get_object_or_404(PostOffice, id=office_id) if office_id else None

        updated_parcel = update_status(
            tracking_number=tracking_number,
            new_status=serializer.validated_data["status"],
            user=request.user,
            office=office,
            comment=serializer.validated_data.get("comment", ""),
        )

        return Response(
            {"status": updated_parcel.status}, status=status.HTTP_201_CREATED
        )


class OfficeParcelsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    serializer_class = ParcelSerializer
    pagination_class = StandardPagination

    def get(self, request, office_id):
        request_office_id = get_object_or_404(PostOffice, id=office_id)

        parcels = Parcel.objects.filter(
            status=Status.ARRIVED,
            current_office_id=request_office_id,
            destination_office_id=request_office_id,
        ).select_related("sender", "recipient", "current_office")

        page = self.paginate_queryset(parcels)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(parcels, many=True)
        return Response(serializer.data)
