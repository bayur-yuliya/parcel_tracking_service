import logging
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

logger = logging.getLogger(__name__)


class Status(models.TextChoices):
    CREATED = "created", "Створено"
    ACCEPTED = "accepted", "Прийнято"
    IN_TRANSIT = "in_transit", "У дорозі"
    ARRIVED = "arrived", "Прибула"
    DELIVERED = "delivered", "Доставлено"
    RETURNED = "returned", "Повернуто"


def get_tracking_number():
    while True:
        number = uuid.uuid4().hex[:12].upper()
        if not Parcel.objects.filter(tracking_number=number).exists():
            return number


class Client(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, related_name="client", null=True, blank=True
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="ПІБ",
    )
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


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.ForeignKey(PostOffice, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.username} ({self.office})"


class Parcel(models.Model):
    tracking_number = models.CharField(
        max_length=15, default=get_tracking_number, unique=True, db_index=True
    )
    sender = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="sent_parcels"
    )
    recipient = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="received_parcels"
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("30.00")),
        ],
        help_text="Вага від 0.01 до 30.00 кг",
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
    current_office = models.ForeignKey(
        PostOffice, on_delete=models.PROTECT, related_name="current_location"
    )
    destination_office = models.ForeignKey(
        PostOffice, related_name="incoming_parcels", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.tracking_number

    def save(self, *args, **kwargs):
        is_created = self.pk is None

        if is_created:
            self.current_office = self.origin_office
            self.status = Status.CREATED

        super().save(*args, **kwargs)

        if is_created:
            ParcelStatusHistory.objects.create(
                parcel=self,
                status=Status.CREATED,
                office=self.origin_office,
                comment="Parcel created",
            )

    class Meta:
        ordering = ["-created_at", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(origin_office=models.F("destination_office")),
                name="origin_not_equal_destination",
            ),
        ]


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
