from django.contrib import admin

from apps.accounts.models import (
    Biller,
    Warehouse,
    Supplier,
)

admin.site.register([Biller, Warehouse, Supplier,])
