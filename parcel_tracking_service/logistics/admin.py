from django.contrib import admin

from .models import ParcelStatusHistory, Parcel, PostOffice, Client

admin.site.register(Client)
admin.site.register(PostOffice)
admin.site.register(Parcel)
admin.site.register(ParcelStatusHistory)
