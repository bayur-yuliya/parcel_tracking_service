import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from .services.services import generate_tracking_number


class Status(models.TextChoices):
    CREATED = "created", "Створено"
    ACCEPTED = "accepted", "Прийнято"
    IN_TRANSIT = "in_transit", "У дорозі"
    ARRIVED = "arrived", "Прибула"
    DELIVERED = "delivered", "Доставлено"
    RETURNED = "returned", "Повернуто"


class Client(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="client", null=True, blank=True
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = PhoneNumberField(
        max_length=13,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name or str(self.phone)


class PostOffice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index = models.CharField(max_length=30, unique=True, db_index=True)
    city = models.CharField(max_length=20, db_index=True)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"№{self.index}, {self.city}"


class Parcel(models.Model):
    tracking_number = models.CharField(
        max_length=15, default=generate_tracking_number, unique=True, db_index=True
    )
    sender = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="sent_parcels"
    )
    recipient = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="received_parcels"
    )
    weight = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    declared_value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CREATED
    )
    origin_office = models.ForeignKey(
        PostOffice, on_delete=models.PROTECT, related_name="outgoing_parcels"
    )
    destination_office = models.ForeignKey(
        PostOffice, related_name="incoming_parcels", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tracking_number

    def save(self, *args, **kwargs):
        is_created = self.pk is None
        super().save(*args, **kwargs)

        if is_created:
            ParcelStatusHistory.objects.create(
                parcel=self,
                status=Status.CREATED,
                office=None,
                comment="Parcel created",
            )


class ParcelStatusHistory(models.Model):
    parcel = models.ForeignKey(
        Parcel, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CREATED
    )
    # null True if parcel created online
    office = models.ForeignKey(
        PostOffice, on_delete=models.SET_NULL, null=True, blank=True
    )
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
