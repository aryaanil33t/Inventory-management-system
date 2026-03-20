from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Sum
from django.db import transaction
from .forms import RackForm
from authentication.permissions import user_role_permission
from .models import Location, Warehouse, Rack, Product, Stock, Order, OrderItem,Cart,CartItem
from invent.models import Supplier

from django.contrib.auth.models import User



@method_decorator(user_role_permission(roles=['Admin'], redirect_url='dashboard'), name='dispatch')
class LocationListView(View):

    template = 'invents/location-list.html'

    def get(self, request, *args, **kwargs):

        locations = Location.objects.all()

        query = request.GET.get('query')

        if query:
            locations = locations.filter(name__icontains=query)

        return render(request, self.template, {'locations': locations})


class AddLocationView(View):

    template_name = "invents/add-location.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        name = request.POST.get("name")

        if name:
            Location.objects.create(name=name)
            return redirect('locations')

        return render(request, self.template_name, {
            "error": "Location name is required"
        })
    
class EditLocationView(View):

    template_name = "invents/edit-location.html"

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')
        location = get_object_or_404(Location, uuid=uuid)

        return render(request, self.template_name, {
            "location": location
        })

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')
        location = get_object_or_404(Location, uuid=uuid)

        name = request.POST.get("name")

        if name:
            location.name = name
            location.save()
            return redirect('locations')

        return render(request, self.template_name, {
            "location": location,
            "error": "Name is required"
        })
    
class DeleteLocationView(View):

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')
        location = get_object_or_404(Location, uuid=uuid)

        location.active_status = False
        location.save()

        return redirect('locations')

@method_decorator(user_role_permission(roles=['Admin'], redirect_url='dashboard'), name='dispatch')


# 🔹 LIST




class WarehouseListView(View):
    template_name = "invent/warehouse-list.html"

    def get(self, request, uuid):
        location = get_object_or_404(Location, uuid=uuid)
        warehouses = Warehouse.objects.filter(location=location, active_status=True)

        # Fetch products for each warehouse
        warehouse_data = []
        for warehouse in warehouses:
            racks = warehouse.racks.filter(active_status=True)
            products = Stock.objects.filter(rack__in=racks).select_related('product', 'rack')
            warehouse_data.append({
                "warehouse": warehouse,
                "products": products
            })

        return render(request, self.template_name, {
            "location": location,
            "warehouse_data": warehouse_data
        })

# 🔹 ADD
class AddWarehouseView(View):

    template_name = "invent/add-warehouse.html"

    def get(self, request, uuid):
        location = get_object_or_404(Location, uuid=uuid)

        return render(request, self.template_name, {
            "location": location
        })

    def post(self, request, uuid):

        location = get_object_or_404(Location, uuid=uuid)
        name = request.POST.get("name")

        if name:
            Warehouse.objects.create(
                name=name,
                location=location
            )
            return redirect('warehouse-list', uuid=location.uuid)

        return render(request, self.template_name, {
            "location": location,
            "error": "Warehouse name is required"
        })


# 🔹 EDIT


class EditWarehouseView(View):
    template_name = "invent/edit-warehouse.html"

    def get(self, request, uuid):
        warehouse = get_object_or_404(Warehouse, uuid=uuid)
        locations = Location.objects.all()  # for the location dropdown
        return render(request, self.template_name, {
            "warehouse": warehouse,
            "locations": locations
        })

    def post(self, request, uuid):
        warehouse = get_object_or_404(Warehouse, uuid=uuid)
        name = request.POST.get("name")
        location_id = request.POST.get("location")  # selected location

        if name and location_id:
            warehouse.name = name
            warehouse.location = get_object_or_404(Location, id=location_id)
            warehouse.save()
            return redirect('warehouse-list', uuid=warehouse.location.uuid)

        locations = Location.objects.all()
        return render(request, self.template_name, {
            "warehouse": warehouse,
            "locations": locations,
            "error": "Name and Location are required"
        })


# 🔹 DELETE (Soft Delete)
class DeleteWarehouseView(View):

    def post(self, request, uuid):

        warehouse = get_object_or_404(Warehouse, uuid=uuid)

        warehouse.active_status = False
        warehouse.save()

        return redirect('warehouse-list', uuid=warehouse.location.uuid)

class RackListView(View):

    template = 'invents/rack-list.html'

    def get(self, request, *args, **kwargs):

        warehouse_uuid = kwargs.get('uuid')

        warehouse = get_object_or_404(Warehouse, uuid=warehouse_uuid)

        racks = Rack.objects.filter(warehouse=warehouse)

        return render(request, self.template, {
            'warehouse': warehouse,
            'racks': racks
        })
    
# Add rack
class RackCreateView(View):
    template = 'invents/rack-form.html'

    def get(self, request, *args, **kwargs):
        warehouse_uuid = kwargs.get('uuid')
        warehouse = get_object_or_404(Warehouse, uuid=warehouse_uuid)
        form = RackForm()
        return render(request, self.template, {'form': form, 'warehouse': warehouse})

    def post(self, request, *args, **kwargs):
        warehouse_uuid = kwargs.get('uuid')
        warehouse = get_object_or_404(Warehouse, uuid=warehouse_uuid)
        form = RackForm(request.POST)
        if form.is_valid():
            rack = form.save(commit=False)
            rack.warehouse = warehouse
            rack.save()
            return redirect('racks', uuid=warehouse.uuid)
        return render(request, self.template, {'form': form, 'warehouse': warehouse})

# Edit rack


class RackUpdateView(View):
    template = 'invents/edit-rack.html'

    def get(self, request, *args, **kwargs):
        rack = get_object_or_404(Rack, uuid=kwargs.get('uuid'))
        form = RackForm(instance=rack)
        return render(request, self.template, {'form': form, 'rack': rack})

    def post(self, request, *args, **kwargs):
        rack = get_object_or_404(Rack, uuid=kwargs.get('uuid'))
        form = RackForm(request.POST, instance=rack)
        if form.is_valid():
            form.save()
            return redirect('racks', uuid=rack.warehouse.uuid)
        return render(request, self.template, {'form': form, 'rack': rack})

# Delete rack
class RackDeleteView(View):
    def post(self, request, *args, **kwargs):
        rack = get_object_or_404(Rack, uuid=kwargs.get('uuid'))
        warehouse_uuid = rack.warehouse.uuid
        rack.delete()
        return redirect('racks', uuid=warehouse_uuid)


class RackProductsView(View):

    template = 'inventory/rack-products.html'

    def get(self, request, *args, **kwargs):

        rack_uuid = kwargs.get('rack_uuid')

        rack = get_object_or_404(Rack, uuid=rack_uuid)

        stocks = Stock.objects.filter(rack=rack).select_related('product')

        return render(request, self.template, {
            'rack': rack,
            'stocks': stocks
        })


class CreateOrderView(View):

    def post(self, request, *args, **kwargs):

        product_ids = request.POST.getlist('selected_products')

        if not product_ids:
            messages.error(request, "No products selected")
            return redirect('dashboard')

        with transaction.atomic():

            order = Order.objects.create(customer=request.user)

            total_amount = 0

            for product_id in product_ids:

                stock = Stock.objects.select_for_update().get(uuid=product_id)

                if stock.quantity <= 0:
                    messages.error(request, f"{stock.product.name} out of stock")
                    return redirect('dashboard')

                stock.quantity -= 1
                stock.save()

                OrderItem.objects.create(
                    order=order,
                    product=stock.product,
                    quantity=1,
                    price=stock.product.selling_price
                )

                total_amount += stock.product.selling_price

        return redirect('order-summary', uuid=order.uuid)


class OrderSummaryView(View):

    template = 'inventory/order-summary.html'

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        order = get_object_or_404(
            Order.objects.prefetch_related('orderitem_set__product'),
            uuid=uuid
        )

        total = order.orderitem_set.aggregate(
            total=Sum('price')
        )['total'] or 0

        return render(request, self.template, {
            'order': order,
            'total': total
        })
    


class AddToCartView(View):
    def post(self, request, uuid):
        product = get_object_or_404(Product, uuid=uuid)

        cart, created = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += 1
            item.save()

        return redirect('cart')
    
class CartView(View):
    template = 'invents/cart.html'

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()

        total = sum(item.total_price() for item in items)

        return render(request, self.template, {
            'items': items,
            'total': total
        })
