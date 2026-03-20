from django.contrib import admin
from . import models


admin.site.register(models.Product)
admin.site.register(models.Category)
admin.site.register(models.Supplier)
admin.site.register(models.Customer)
admin.site.register(models.Purchase)
admin.site.register(models.PurchaseItem)
admin.site.register(models.Sale)
admin.site.register(models.SaleItem)
