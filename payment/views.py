from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from authentication.permissions import user_role_permission
from decouple import config
import razorpay
from weasyprint import HTML
from django.db.models import Sum
from django.utils.decorators import method_decorator
from invent.models import Product, Sale, SaleItem, Customer,Purchase
from invents.models import Order as InventOrder, OrderItem, Stock
from payment.models import Order, PaymentStatusChoices
from .models import Payment, Transaction
from invents.views import Cart,CartItem

# ----------------------------------
# CREATE PAYMENT
# ----------------------------------
@method_decorator(user_role_permission(roles=['User'], redirect_url='dashboard'), name='dispatch')
class CreatePaymentView(View):

    def get(self, request, *args, **kwargs):

        product_uuid = kwargs.get("uuid")
        quantity = int(request.GET.get("quantity", 1))
        product = Product.objects.get(uuid=product_uuid)
        stock = Stock.objects.filter(product=product).aggregate(total=Sum("quantity"))
        current_stock = stock["total"] if stock["total"] else 0

        if current_stock < quantity:
            messages.error(request, "Product Out Of Stock")
            return redirect("product-detail", uuid=product.uuid)

        total_amount = product.selling_price * quantity

        # Order
        order = Order.objects.create(
            customer=request.user
        )

        # Order Item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.selling_price
        )

        # Payment
        payment = Payment.objects.create(
            order=order,
            amount=total_amount
        )

        # Razorpay Client
        client = razorpay.Client(
            auth=(config('RZP_KEY_ID'), config('RZP_KEY_SECRETE'))
        )

        rzp_order = client.order.create({
            "amount": int(total_amount * 100),
            "currency": "INR"
        })

        # Transaction
        transaction = Transaction.objects.create(
            payment=payment,
            gateway_order_id=rzp_order['id'],
            amount=total_amount
        )

        # Redirect to Razorpay page
        return redirect("razorpay", uuid=transaction.uuid)


# ----------------------------------
# RAZORPAY PAYMENT PAGE
# ----------------------------------
@method_decorator(user_role_permission(roles=['User'], redirect_url='dashboard'), name='dispatch')
class RazorpayView(View):
    template = 'payment/razorpay.html'

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        transaction = Transaction.objects.get(uuid=uuid)
        context = {
            "RZP_KEY_ID": config("RZP_KEY_ID"),
            "amount": int(transaction.amount * 100),
            "rzp_order_id": transaction.gateway_order_id
        }
        return render(request, self.template, context)


# ----------------------------------
# PAYMENT VERIFY
# ----------------------------------
@method_decorator(user_role_permission(roles=['User'], redirect_url='dashboard'), name='dispatch')
class PaymentVerifyView(View):

    def post(self, request, *args, **kwargs):

        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        transaction = Transaction.objects.get(
            gateway_order_id=razorpay_order_id
        )

        client = razorpay.Client(
            auth=(config('RZP_KEY_ID'), config('RZP_KEY_SECRETE'))
        )

        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })

        # --------------------------------
        # SAVE PAYMENT DETAILS
        # --------------------------------
        transaction.gateway_payment_id = razorpay_payment_id
        transaction.gateway_signature = razorpay_signature
        transaction.status = PaymentStatusChoices.COMPLETED
        transaction.transaction_at = timezone.now()

        transaction.payment.status = PaymentStatusChoices.COMPLETED
        transaction.payment.paid_at = timezone.now()

        transaction.save()
        transaction.payment.save()

        # --------------------------------
        # UPDATE ORDER STATUS
        # --------------------------------
        order = transaction.payment.order
        order.status = PaymentStatusChoices.COMPLETED
        order.save()

        # --------------------------------
        # REDUCE STOCK (RACK-WISE)
        # --------------------------------
        for item in order.orderitem_set.all():

            required_qty = item.quantity
            stocks = Stock.objects.filter(product=item.product).order_by('created_at')

            for stock in stocks:
                if required_qty <= 0:
                    break
                if stock.quantity >= required_qty:
                    stock.quantity -= required_qty
                    stock.save()
                    required_qty = 0
                else:
                    required_qty -= stock.quantity
                    stock.quantity = 0
                    stock.save()

        # --------------------------------
        # CREATE SALE RECORD
        # --------------------------------
        # Fix: Assign a Customer instance, not Profile/User
        # Use logged-in user
        profile = request.user  # Profile/User object
        customer_email = profile.email  # must be set

# Make sure email exists
        if not customer_email:
            customer_email = f"{profile.username}@example.com"  # fallback

        customer, created = Customer.objects.get_or_create(
            email=customer_email,
            defaults={
        'name': profile.username,
        'phone': '',
        'address': ''
    }
)

        sale = Sale.objects.create(
            customer=customer,
            invoice_number=f"INV{Sale.objects.count() + 1}",
            sale_date=timezone.now().date()
        )

        for item in order.orderitem_set.all():
            SaleItem.objects.create(
                sale=sale,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )

        # --------------------------------
        # SUCCESS MESSAGE
        # --------------------------------
        messages.success(request, "Payment Successfully Completed")

        # CLEAR CART AFTER SUCCESS
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

        return redirect('invoice', uuid=transaction.uuid)


# ----------------------------------
# INVOICE PAGE
# ----------------------------------
@method_decorator(user_role_permission(roles=['User'], redirect_url='dashboard'), name='dispatch')
class InvoiceView(View):
    template = 'payment/invoice.html'

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        transaction = Transaction.objects.get(uuid=uuid)
        return render(request, self.template, context={'transaction': transaction})


# ----------------------------------
# INVOICE PDF GENERATOR
# ----------------------------------
@method_decorator(user_role_permission(roles=['User'], redirect_url='dashboard'), name='dispatch')
class InvoicePDFGenerator(View):

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        transaction = Transaction.objects.select_related(
            "payment",
            "payment__order",
            "payment__order__customer"
        ).prefetch_related(
            "payment__order__orderitem_set",
            "payment__order__orderitem_set__product"
        ).get(uuid=uuid)

        html = render_to_string("payment/invoice-pdf.html", {'transaction': transaction})
        pdf = HTML(string=html)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice-{transaction.payment.order.id}.pdf"'
        pdf.write_pdf(response)

        return response


# ----------------------------------
# MY ORDERS VIEW
# ----------------------------------
class MyOrdersView(View):
    template_name = "payment/my-orders.html"

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(
            customer=request.user
        ).exclude(
            status=PaymentStatusChoices.CANCELLED
        ).prefetch_related(
            "orderitem_set",
            "orderitem_set__product",
            "payment",
            "payment__transactions"
        ).order_by('-created_at')

        return render(request, self.template_name, {'orders': orders})


# ----------------------------------
# CANCEL ORDER
# ----------------------------------
class CancelOrderView(View):

    def post(self, request, *args, **kwargs):
        order_id = kwargs.get("order_id")
        order = Order.objects.get(id=order_id, customer=request.user)

        if order.status == PaymentStatusChoices.COMPLETED:
            messages.error(request, "Cannot cancel a paid order")
            return redirect("my-orders")

        for item in order.orderitem_set.all():
            stock = Stock.objects.filter(product=item.product).first()
            if stock:
                stock.quantity += item.quantity
                stock.save()

        order.status = PaymentStatusChoices.CANCELLED
        order.save()
        messages.success(request, "Order Cancelled Successfully")

        return redirect("my-orders")



# --------------------------
# PURCHASE STATEMENT PDF
# --------------------------
class PurchaseStatementPDF(View):

    def get(self, request, *args, **kwargs):
        purchases = Purchase.objects.prefetch_related('products', 'purchaseitem_set').order_by('-purchase_date')

        context = {
            'purchases': purchases
        }

        html_string = render_to_string('invent/purchase-statement.html', context)
        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="purchase-statement.pdf"'
        return response


# --------------------------
# SALES STATEMENT PDF
# --------------------------
class SalesStatementPDF(View):

    def get(self, request, *args, **kwargs):
        sales = Sale.objects.prefetch_related('products', 'saleitem_set').order_by('-sale_date')

        context = {
            'sales': sales
        }

        html_string = render_to_string('invent/sales-statement.html', context)
        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="sales-statement.pdf"'
        return response


class CreateCartPaymentView(View):

    def get(self, request, *args, **kwargs):

        cart = Cart.objects.get(user=request.user)
        items = cart.items.all()

        if not items:
            messages.error(request, "Cart is empty")
            return redirect('cart')

        total_amount = 0

        # CREATE ORDER
        order = Order.objects.create(
            customer=request.user
        )

        # CREATE ORDER ITEMS
        for item in items:
            product = item.product

            stock = Stock.objects.filter(product=product).aggregate(total=Sum("quantity"))
            current_stock = stock["total"] if stock["total"] else 0

            if current_stock < item.quantity:
                messages.error(request, f"{product.name} is out of stock")
                return redirect('cart')

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.selling_price
            )

            total_amount += product.selling_price * item.quantity

        # CREATE PAYMENT
        payment = Payment.objects.create(
            order=order,
            amount=total_amount
        )

        # RAZORPAY
        client = razorpay.Client(
            auth=(config('RZP_KEY_ID'), config('RZP_KEY_SECRETE'))
        )

        rzp_order = client.order.create({
            "amount": int(total_amount * 100),
            "currency": "INR"
        })

        transaction = Transaction.objects.create(
            payment=payment,
            gateway_order_id=rzp_order['id'],
            amount=total_amount
        )

        return redirect("razorpay", uuid=transaction.uuid)