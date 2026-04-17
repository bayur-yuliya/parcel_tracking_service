import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from ...models import Client, PostOffice, Parcel, Status, ParcelStatusHistory


class Command(BaseCommand):
    help = "Seed database with test data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        cities = [
            "Київ",
            "Львів",
            "Одеса",
            "Харків",
            "Дніпро",
            "Запоріжжя",
        ]

        offices = []
        for city in cities:
            for i in range(1, 4):
                office, _ = PostOffice.objects.get_or_create(
                    index=f"{city[:2].upper()}-{i}",
                    defaults={
                        "city": city,
                        "address": f"Вулиця {i}, {city}",
                    },
                )
                offices.append(office)

        self.stdout.write(f"Created {len(offices)} offices")

        clients = []

        for i in range(10):
            user = User.objects.create_user(
                username=f"user{i}",
                password="password123",
            )

            client = Client.objects.create(
                user=user,
                full_name=f"Користувач {i}",
                phone=f"+380000000{i:02}",
            )
            clients.append(client)

        self.stdout.write(f"Created {len(clients)} clients")

        parcels = []

        for i in range(20):
            sender, recipient = random.sample(clients, 2)

            origin = random.choice(offices)
            destination = random.choice([o for o in offices if o != origin])

            parcel = Parcel.objects.create(
                sender=sender,
                recipient=recipient,
                weight=Decimal(random.uniform(0.5, 10)).quantize(Decimal("0.01")),
                declared_value=Decimal(random.randint(100, 10000)),
                origin_office=origin,
                current_office=origin,
                destination_office=destination,
            )

            parcels.append(parcel)

        self.stdout.write(f"Created {len(parcels)} parcels")

        for parcel in parcels:
            statuses_flow = [
                Status.ACCEPTED,
                Status.IN_TRANSIT,
                Status.ARRIVED,
            ]

            for status in statuses_flow:
                if random.choice([True, False]):
                    office = random.choice(offices)

                    ParcelStatusHistory.objects.create(
                        parcel=parcel,
                        status=status,
                        office=office,
                        comment=f"Auto update: {status}",
                    )

                    parcel.status = status
                    parcel.current_office = office
                    parcel.save(skip_clean=True)

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))
