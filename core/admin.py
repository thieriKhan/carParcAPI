from django.contrib import admin

from core.models import *

# Register your models here.
admin.site.register(Mouvment)
admin.site.register(Invoice)
admin.site.register(InvoiceDetail)
admin.site.register(VehicleType)
admin.site.register(TVA)
admin.site.register(LinePrice)