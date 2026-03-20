from django.urls import path
from .views import (
    HomeView,
    ProductCreateView,
    ProductDetailView,
    ProductEditView,
    ProductDeleteView,
    CategoryListView,SupplierListView,PurchaseListView,SalesListView,AddSupplierView,SupplierEditView,DeleteSupplierView,PurchaseDetailView,SaleDetailView,
    CategoryAddView,CategoryEditView,CategoryDeleteView,CategoryProductsView
    
)

urlpatterns = [
    path('', HomeView.as_view(), name='dashboard'),
    path('products/', HomeView.as_view(), name='product-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('suppliers/', SupplierListView.as_view(), name='suppliers-list'),
    path('add-supplier/', AddSupplierView.as_view(), name='add-supplier'),
    path('supplier/<uuid:uuid>/edit/', SupplierEditView.as_view(), name='edit-supplier'),
    path('supplier/<uuid:uuid>/delete/', DeleteSupplierView.as_view(), name='delete-supplier'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/add/', CategoryAddView.as_view(), name='category-add'),
    path('categories/edit/<uuid:uuid>/', CategoryEditView.as_view(), name='category-edit'),
    path('categories/delete/<uuid:uuid>/', CategoryDeleteView.as_view(), name='category-delete'),
    path('categories/<uuid:uuid>/', CategoryProductsView.as_view(), name='category-products'),

    # Purchases
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/detail/', PurchaseDetailView.as_view(), name='purchase-detail'),

    # Sales
    path('sales/', SalesListView.as_view(), name='sales-list'),
    path('sales/detail/', SaleDetailView.as_view(), name='sale-detail'),

    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('product/<uuid:uuid>/detail/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<uuid:uuid>/edit/', ProductEditView.as_view(), name='product-edit'),
    path('product/<uuid:uuid>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]