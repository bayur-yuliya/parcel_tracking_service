from django.urls import path

from logistics.api.v1.views import (
    ParcelDetailView,
    ParcelUpdateStatusView,
    OfficeParcelsView,
    ParcelListCreateView,
)

urlpatterns = [
    path("parcels/", ParcelListCreateView.as_view()),
    path("parcels/<str:tracking_number>/", ParcelDetailView.as_view()),
    path("parcels/<str:tracking_number>/status/", ParcelUpdateStatusView.as_view()),
    path("offices/<str:office_id>/parcels/", OfficeParcelsView.as_view()),
]
