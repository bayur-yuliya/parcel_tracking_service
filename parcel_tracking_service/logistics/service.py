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
            parcel = Parcel.objects.select_for_update().get(
                tracking_number=tracking_number
            )
            current_status = parcel.status
            employee = user.employee

            if office and office != employee.office:
                raise ValidationError("Ви можете працювати тільки зі своїм відділенням")

            if current_status in FINAL_STATUSES:
                raise ValidationError("Статус уже фінальний, зміна неможлива")

            allowed = ALLOWED_TRANSITIONS.get(current_status, [])

            if new_status not in allowed:
                raise ValidationError(
                    f"Не можна перейти з {current_status} в {new_status}"
                )

            if new_status == Status.DELIVERED:
                check_office = office or parcel.current_office
                if check_office != parcel.destination_office:
                    raise ValidationError(
                        "Посилку можна видати лише у відділенні призначення."
                    )

            parcel.status = new_status

            if office:
                parcel.current_office = office

            parcel.save(update_fields=["status", "current_office"])

            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=new_status,
                office=office,
                comment=comment,
            )

        logger.info(
            f"Successfully updated parcel {tracking_number} to {new_status} at office {office}"
        )
        return parcel
    except ValidationError as e:
        logger.warning(f"Validation failed for parcel {tracking_number}: {e}")
        raise
    except Exception as e:
        logger.error(f"Critical system error: {e}", exc_info=True)
        raise
