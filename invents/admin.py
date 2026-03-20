from django.contrib import admin
from . import models


admin.site.register(models.Location)
admin.site.register(models.Warehouse)
admin.site.register(models.Rack)
admin.site.register(models.Category)
admin.site.register(models.Stock)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
