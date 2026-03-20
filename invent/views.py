from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q
from django.utils.decorators import method_decorator
from datetime import date
from .models import Product, Category,Supplier,Purchase,Sale,SaleItem,PurchaseItem,Customer
from invents.models import Stock
from django.db.models import Sum

from .forms import ProductForm,SupplierForm
from authentication.permissions import user_role_permission




class HomeView(View):

    template = 'invent/home.html'

    def get(self, request, *args, **kwargs):

        query = request.GET.get('query', '').strip()

        products = Product.objects.filter(active_status=True)

        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(supplier__name__icontains=query)
            ).distinct()

        print("FINAL PRODUCTS:", products)

        return render(request, self.template, {
            'products': products,
            'query': query,
            'page': 'Products'
        })
# ------------------------
# List Categories
# ------------------------
class CategoryListView(View):
    template = 'invent/category-list.html'

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, self.template, {'categories': categories, 'page': 'Categories'})

# ------------------------
# Add Category
# ------------------------
@method_decorator(user_role_permission(roles=['Admin'], redirect_url='category-list'), name='dispatch')
class CategoryAddView(View):
    template = 'invent/category-form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        if name:
            category = Category.objects.create(name=name)
            
            return redirect('category-list')
        return render(request, self.template, {'error': 'Name is required'})

# ------------------------
# Edit Category
# ------------------------
@method_decorator(user_role_permission(roles=['Admin'], redirect_url='category-list'), name='dispatch')
class CategoryEditView(View):
    template = 'invent/category-form.html'

    def get(self, request, uuid, *args, **kwargs):
        category = get_object_or_404(Category, uuid=uuid)
        return render(request, self.template, {'category': category})

    def post(self, request, uuid, *args, **kwargs):
        category = get_object_or_404(Category, uuid=uuid)
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
          
            return redirect('category-list')
        return render(request, self.template, {'category': category, 'error': 'Name is required'})

# ------------------------
# Delete Category
# ------------------------
@method_decorator(user_role_permission(roles=['Admin'], redirect_url='category-list'), name='dispatch')
class CategoryDeleteView(View):
    def post(self, request, uuid, *args, **kwargs):
        category = get_object_or_404(Category, uuid=uuid)
        category.delete()
    
        return redirect('category-list')
    



class CategoryProductsView(View):
    template_name = 'invent/category-products.html'

    def get(self, request, uuid, *args, **kwargs):
        category = get_object_or_404(Category, uuid=uuid)
        products = Product.objects.filter(category=category, active_status=True)

        context = {
            'category': category,
            'products': products,
            'page': category.name
        }
        return render(request, self.template_name, context)
    

class SupplierListView(View):

    template_name = "invent/suppliers-list.html"

    def get(self, request):

        # ✅ Only show active suppliers
        suppliers = Supplier.objects.filter(active_status=True)

        print("SUPPLIERS:", suppliers)

        return render(request, self.template_name, {
            "suppliers": suppliers
        })
class AddSupplierView(View):

    template_name = "invent/add-supplier.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        company_name = request.POST.get("company_name")

        Supplier.objects.create(
            name=name,
            email=email,
            phone=phone,
            company_name=company_name
        )

        
        return redirect("suppliers-list")
    




class SupplierEditView(View):

    template = 'invent/supplier-edit.html'
    form_class = SupplierForm

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        supplier = get_object_or_404(Supplier, uuid=uuid)

        form = self.form_class(instance=supplier)

        return render(request, self.template, {
            'form': form,
            'page': 'Edit Supplier'
        })

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        supplier = get_object_or_404(Supplier, uuid=uuid)

        form = self.form_class(request.POST, instance=supplier)

        if form.is_valid():
            form.save()
            return redirect('suppliers-list')

        return render(request, self.template, {
            'form': form,
            'page': 'Edit Supplier'
        })
    
    
class DeleteSupplierView(View):

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        supplier = get_object_or_404(Supplier, uuid=uuid)

        supplier.active_status = False
        supplier.save()

        return redirect('suppliers-list')
 

# -------------------------------
# Purchase List
# -------------------------------
class PurchaseListView(View):
    template_name = 'invent/purchase-list.html'

    def get(self, request):
        purchases = Purchase.objects.all().order_by('-purchase_date')
        return render(request, self.template_name, {'purchases': purchases})

# -------------------------------
# Purchase Detail (invoice_number via GET)
# -------------------------------
class PurchaseDetailView(View):
    template_name = 'invent/purchase-detail.html'

    def get(self, request):
        invoice_number = request.GET.get('invoice_number')
        purchase = get_object_or_404(Purchase, invoice_number=invoice_number)
        items = PurchaseItem.objects.filter(purchase=purchase)
        return render(request, self.template_name, {'purchase': purchase, 'items': items})

# -------------------------------
# Sales List
# -------------------------------

class SalesListView(View):
    template_name = 'invent/sale-list.html'

    def get(self, request):
        sales = Sale.objects.all().order_by('-sale_date')
        return render(request, self.template_name, {'sales': sales, 'page': 'Sales List'})


class SaleDetailView(View):
    template_name = 'invent/sale-detail.html'

    def get(self, request):
        invoice_number = request.GET.get('invoice_number')
        sale = get_object_or_404(Sale, invoice_number=invoice_number)
        items = SaleItem.objects.filter(sale=sale)
        return render(request, self.template_name, {'sale': sale, 'items': items, 'page': 'Sale Detail'})


# Function to create sale after payment (simulate checkout)
def create_sale(request):
    # Example: assume customer_id is 1, cart_items simulated
    customer = Customer.objects.first()  # replace with request.user.customer if linked
    cart_items = [
        {'product_id': 1, 'quantity': 2, 'price': 100},
        {'product_id': 2, 'quantity': 1, 'price': 50},
    ]

    sale = Sale.objects.create(
        customer=customer,
        invoice_number=f"INV{Sale.objects.count() + 1}",
        sale_date=date.today()
    )

    for item in cart_items:
        product = Product.objects.get(id=item['product_id'])
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=item['quantity'],
            price=item['price']
        )

    return redirect('sales-list')


@method_decorator(user_role_permission(roles=['Admin'], redirect_url='product-list'), name='dispatch')
class ProductCreateView(View):

    template = 'invent/product-create.html'
    form_class = ProductForm

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        return render(request, self.template, {
            'form': form,
            'page': 'Create Product'
        })

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('product-list')

        return render(request, self.template, {
            'form': form,
            'page': 'Create Product'
        })





class ProductDetailView(View):
    template = "invent/product-detail.html"

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        product = Product.objects.get(uuid=uuid)

        # ✅ FIXED STOCK CALCULATION
        stock_data = Stock.objects.filter(product=product).aggregate(total=Sum("quantity"))
        current_stock = stock_data["total"] or 0

        context = {
            "product": product,
            "current_stock": current_stock
        }
        
        return render(request, self.template, context)

@method_decorator(user_role_permission(roles=['Admin'], redirect_url='product-list'), name='dispatch')
class ProductEditView(View):

    template = 'invent/product-edit.html'
    form_class = ProductForm

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        product = get_object_or_404(Product, uuid=uuid)

        form = self.form_class(instance=product)

        return render(request, self.template, {
            'form': form,
            'page': 'Edit Product'
        })

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        product = get_object_or_404(Product, uuid=uuid)

        form = self.form_class(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('product-list')

        return render(request, self.template, {
            'form': form,
            'page': 'Edit Product'
        })


@method_decorator(user_role_permission(roles=['Admin'], redirect_url='product-list'), name='dispatch')
class ProductDeleteView(View):

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        product = get_object_or_404(Product, uuid=uuid)

        product.active_status = False
        product.save()

        return redirect('product-list')