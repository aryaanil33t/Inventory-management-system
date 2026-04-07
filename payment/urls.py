from django.urls import path
from . import views

urlpatterns = [

    path('buy-product/<uuid:uuid>/', views.CreatePaymentView.as_view(), name='buy-product'),

    path('razorpay/<uuid:uuid>/', views.RazorpayView.as_view(), name='razorpay'),

    path('payment-verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),

    path('invoice/<uuid:uuid>/', views.InvoiceView.as_view(), name='invoice'),

    path('invoice-pdf/<uuid:uuid>/', views.InvoicePDFGenerator.as_view(), name='invoice-pdf'),

    path("my-orders/", views.MyOrdersView.as_view(), name="my-orders"),

    path("cancel-order/<int:order_id>/", views.CancelOrderView.as_view(), name="cancel-order"),

    path('purchases/pdf/', views.PurchaseStatementPDF.as_view(), name='purchase-statement-pdf'),
    path('sales/pdf/', views.SalesStatementPDF.as_view(), name='sales-statement-pdf'),
    path('cart-checkout/', views.CreateCartPaymentView.as_view(), name='cart-checkout'),
]