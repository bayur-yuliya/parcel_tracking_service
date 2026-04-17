from django_filters.rest_framework import FilterSet, filters

from logistics.models import Parcel


class ParcelFilter(FilterSet):
    from_city = filters.CharFilter(
        field_name="origin_office__city", lookup_expr="iexact"
    )

    class Meta:
        model = Parcel
        fields = ["status", "from_city"]
