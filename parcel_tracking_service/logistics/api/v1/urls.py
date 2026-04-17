from django.urls import path
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularAPIView,
    SpectacularRedocView,
)

from logistics.api.v1.views import (
    ParcelDetailView,
    ParcelUpdateStatusView,
    OfficeParcelsView,
    ParcelListCreateView,
)

urlpatterns = [
    # Raw OpenAPI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # parcels urls
    path("parcels/", ParcelListCreateView.as_view()),
    path("parcels/<str:tracking_number>/", ParcelDetailView.as_view()),
    path("parcels/<str:tracking_number>/status/", ParcelUpdateStatusView.as_view()),
    path("offices/<str:office_id>/parcels/", OfficeParcelsView.as_view()),
]
