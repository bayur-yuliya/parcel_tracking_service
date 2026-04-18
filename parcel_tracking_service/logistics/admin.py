from django.contrib import admin
from .models import Client, PostOffice, Parcel, ParcelStatusHistory


class ParcelStatusHistoryInline(admin.TabularInline):
    model = ParcelStatusHistory
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("status", "office", "comment", "created_at")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "user", "is_active")
    search_fields = ("full_name", "phone")
    list_filter = ("is_active",)
    list_editable = ("is_active",)


@admin.register(PostOffice)
class PostOfficeAdmin(admin.ModelAdmin):
    list_display = ("index", "city", "address")
    search_fields = ("index", "city", "address")
    list_filter = ("city",)


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "sender",
        "recipient",
        "status",
        "current_office",
        "weight",
        "created_at",
    )

    search_fields = (
        "tracking_number",
        "sender__full_name",
        "recipient__full_name",
        "sender__phone",
    )

    list_filter = ("status", "origin_office", "destination_office", "created_at")

    inlines = [ParcelStatusHistoryInline]

    readonly_fields = ("tracking_number", "created_at")

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("tracking_number", "status", "created_at")},
        ),
        ("Участники", {"fields": ("sender", "recipient")}),
        ("Параметры груза", {"fields": ("weight", "declared_value")}),
        (
            "Логистика",
            {"fields": ("origin_office", "current_office", "destination_office")},
        ),
    )


@admin.register(ParcelStatusHistory)
class ParcelStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("parcel", "status", "office", "created_at")
    list_filter = ("status", "created_at", "office")
    search_fields = ("parcel__tracking_number",)
    readonly_fields = ("created_at",)
