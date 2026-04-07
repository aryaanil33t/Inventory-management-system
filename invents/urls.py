from django.urls import path
from . import views

urlpatterns = [

    # 🔹 Locations
    path('locations/', views.LocationListView.as_view(), name='locations'),

    path('add-location/', views.AddLocationView.as_view(), name='add-location'),

    # EDIT → needs UUID
    path('location/<uuid:uuid>/edit/', views.EditLocationView.as_view(), name='edit-location'),

    # DELETE → needs UUID
    path('location/<uuid:uuid>/delete/', views.DeleteLocationView.as_view(), name='delete-location'),

    # 🔹 Warehouses under a location
   path('warehouse-list/<uuid:uuid>/', views.WarehouseListView.as_view(), name='warehouse-list'),

    path('warehouse/add/<uuid:uuid>/', views.AddWarehouseView.as_view(), name='add-warehouse'),

    path('warehouse/<uuid:uuid>/edit/', views.EditWarehouseView.as_view(), name='edit-warehouse'),

    path('warehouse/<uuid:uuid>/delete/', views.DeleteWarehouseView.as_view(), name='delete-warehouse'),

    # 🔹 Racks under a warehouse
    path('racks/<str:uuid>/', views.RackListView.as_view(), name='racks'),

    path('warehouse/<uuid:uuid>/racks/add/', views.RackCreateView.as_view(), name='add-rack'),
    path('racks/<uuid:uuid>/edit/', views.RackUpdateView.as_view(), name='edit-rack'),
    path('racks/<uuid:uuid>/delete/', views.RackDeleteView.as_view(), name='delete-rack'),


    # 🔹 Products inside a rack
    path('rack-products/<str:rack_uuid>/', views.RackProductsView.as_view(), name='rack-products'),

    # 🔹 Create Order
    path('create-order/', views.CreateOrderView.as_view(), name='create-order'),

    # 🔹 Order Summary
    path('order-summary/<str:uuid>/', views.OrderSummaryView.as_view(), name='order-summary'),

    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<uuid:uuid>/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('remove-item/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove-item'),
    

]
