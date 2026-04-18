import logging
from rest_framework.exceptions import ValidationError
from django.db import transaction

from logistics.models import Status, ParcelStatusHistory, Parcel

logger = logging.getLogger(__name__)

ALLOWED_TRANSITIONS = {
    Status.CREATED: [Status.ACCEPTED],
    Status.ACCEPTED: [Status.IN_TRANSIT],
    Status.IN_TRANSIT: [Status.ARRIVED],
    Status.ARRIVED: [Status.DELIVERED, Status.RETURNED],
}
FINAL_STATUSES = [Status.DELIVERED, Status.RETURNED]


def update_status(tracking_number, new_status, user, office=None, comment=""):
    try:
        with transaction.atomic():
            parcel = (
                Parcel.objects.select_for_update()
                .select_related("destination_office", "current_office", "origin_office")
                .get(tracking_number=tracking_number)
            )

            current_status = parcel.status

            if current_status == new_status:
                return parcel

            if not hasattr(user, "employee"):
                raise ValidationError("Користувач не є працівником відділення")

            employee = user.employee

            if office is None:
                raise ValidationError("Відділення обов'язкове")

            if office != employee.office:
                raise ValidationError("Ви можете працювати тільки зі своїм відділенням")

            if current_status in FINAL_STATUSES:
                raise ValidationError("Статус уже фінальний, зміна неможлива")

            allowed = ALLOWED_TRANSITIONS.get(current_status, [])
            if new_status not in allowed:
                raise ValidationError(
                    f"Не можна перейти з {current_status} в {new_status}"
                )

            check_office_restrictions(parcel, new_status, office)

            parcel.status = new_status
            parcel.current_office = office
            parcel.save(update_fields=["status", "current_office"])

            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=new_status,
                office=office,
                comment=comment,
            )

        logger.info(f"Parcel {tracking_number} -> {new_status} at office {office.id}")
        return parcel

    except Parcel.DoesNotExist:
        logger.warning(f"Parcel not found: {tracking_number}")
        raise ValidationError("Посилка не знайдена")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(
            f"Critical system error updating parcel {tracking_number}: {e}",
            exc_info=True,
        )
        raise


def check_office_restrictions(parcel, new_status, office):
    if new_status == Status.ACCEPTED and office != parcel.origin_office:
        raise ValidationError("Посилку можна прийняти тільки у відділенні відправлення")

    if (
        new_status in [Status.ARRIVED, Status.DELIVERED]
        and office != parcel.destination_office
    ):
        error_msg = (
            "Посилка може прибути тільки у відділення призначення"
            if new_status == Status.ARRIVED
            else "Посилку можна видати лише у відділенні призначення"
        )
        raise ValidationError(error_msg)
