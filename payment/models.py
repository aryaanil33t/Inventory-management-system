from django.db import models
from django.utils import timezone
from invent.models import Baseclass
from invents.models import PaymentStatusChoices
from invents.models import Order



class Payment(Baseclass):
    """
    Represents a payment attempt for an order
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )

    paid_at = models.DateTimeField(null=True, blank=True)

    def mark_as_paid(self):
        """
        Mark payment as successful and reduce stock
        """
        if self.status != PaymentStatusChoices.SUCCESS:
            self.status = PaymentStatusChoices.SUCCESS
            self.paid_at = timezone.now()
            self.save()
            self.order.reduce_stock()
            self.order.mark_completed()

    def __str__(self):
        return f'Payment - Order #{self.order.id} - {self.status}'

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

class Transaction(Baseclass):
    """
    Stores gateway-level transaction details
    """

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    gateway_order_id = models.CharField(max_length=100)
    gateway_payment_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_signature = models.TextField(null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING
    )

    transaction_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Transaction {self.gateway_order_id} - {self.status}'

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


# Create your models here.
