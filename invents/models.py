from django.db import models
from invent.models import Baseclass
from invent.models import Product
from django.conf import settings
   # your abstract base model


# 🔹 Location (City / Area)
class Location(Baseclass):
    name = models.CharField(max_length=100)
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Warehouse(Baseclass):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='warehouses'
    )
    active_status = models.BooleanField(default=True)

    class Meta:
        unique_together = ['name', 'location']

    def __str__(self):
        return f"{self.name} ({self.location.name})"


class Rack(Baseclass):
    name = models.CharField(max_length=50)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='racks'
    )
    capacity = models.IntegerField(null=True, blank=True)
    active_status = models.BooleanField(default=True)

    class Meta:
        unique_together = ['name', 'warehouse']

    def __str__(self):
        return f"{self.name} ({self.warehouse.name})"


# 🔹 Category
class Category(Baseclass):

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name




# 🔹 Stock (like Seat)
class Stock(Baseclass):
    product = models.ForeignKey('invent.Product', on_delete=models.CASCADE)  # ✅ ADD THIS
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ('product', 'rack')

    def __str__(self):
        return f"{self.product.name} - {self.rack.name} - Qty:{self.quantity}"


# 🔹 Order Status
class PaymentStatusChoices(models.TextChoices):

    PENDING = "Pending", "Pending"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"


# 🔹 Orders (like Booking)
class Order(Baseclass):

    customer = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.customer.first_name} - {self.status}"


# 🔹 Order Items (important for production systems)
class OrderItem(Baseclass):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    @property
    def total_price(self):
        return self.quantity * self.price
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.selling_price * self.quantity