from django.contrib import admin

# Register your models here.
from .models import SaleAnnouncement, Photo

admin.site.register(SaleAnnouncement)
admin.site.register(Photo)
