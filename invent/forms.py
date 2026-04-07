from django import forms
from .models import Category, Supplier, Customer, Product, Purchase, Sale
from invents.models import Stock



# ===============================
# 🔹 Category Form
# ===============================

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        exclude = ['uuid', 'active_status']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category Name'
            }),
        }


# ===============================
# 🔹 Supplier Form
# ===============================

class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        exclude = ['uuid', 'created_at', 'updated_at']


# ===============================
# 🔹 Customer Form
# ===============================

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        exclude = ['uuid', 'active_status']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 3
            }),
        }


# ===============================
# 🔹 Product Form
# ===============================

class ProductForm(forms.ModelForm):
    
    quantity = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class':'form-control',
            'placeholder':'Stock Quantity'
        })
    )

    class Meta:
        model = Product

        fields = [
            'name',
            'description',
            'sku',
            'category',
            'supplier',
            'purchase_price',
            'selling_price',
            
            'product_image'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Product Description',
                'rows': 4
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU Code'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Purchase Price'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Selling Price'
            }),

            'product_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


# ===============================
# 🔹 Purchase Form
# ===============================

class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        exclude = ['uuid', 'active_status']

        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice Number'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


# ===============================
# 🔹 Sale Form
# ===============================

class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        exclude = ['uuid', 'active_status']

        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Invoice Number'
            }),
            'sale_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
