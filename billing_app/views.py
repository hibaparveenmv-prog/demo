from django.shortcuts import render 
from.models import Product, Bill, Billitem
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation

@login_required
def dashboard(request):
    Products = Product.objects.all()
    return render(request,'dashboard.html', {'products': Products})
@login_required
def create_bill(request):
    products = Product.objects.all()
    if request.method == "POST":
        customer = request.POST.get('customer', '').strip()
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')
        discount_input = request.POST.get('discount', '0').strip() or '0'
        error = None
        items = []

        if not customer:
            error = 'Customer name is required.'

        try:
            discount = Decimal(discount_input)
            if discount < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            error = 'Discount must be a valid non-negative number.'

        if error is None:
            if not product_ids or not quantities or len(product_ids) != len(quantities):
                error = 'Please add at least one product.'

        if error is None:
            for index, (product_id, quantity_value) in enumerate(zip(product_ids, quantities), start=1):
                if not product_id:
                    error = f'Please select a product for row {index}.'
                    break
                try:
                    quantity = int(quantity_value)
                except ValueError:
                    error = f'Quantity for row {index} must be a whole number.'
                    break
                if quantity <= 0:
                    error = f'Quantity for row {index} must be at least 1.'
                    break
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    error = f'Selected product for row {index} is invalid.'
                    break

                subtotal = Decimal(str(product.price)) * quantity
                gst_amount = subtotal * (Decimal(str(product.gst)) / Decimal('100'))
                line_total = subtotal + gst_amount

                items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal,
                    'gst_amount': gst_amount,
                    'line_total': line_total,
                })

            if not items and error is None:
                error = 'Please add at least one product.'

        if error is None:
            out_of_stock = [item for item in items if item['product'].stock < item['quantity']]
            if out_of_stock:
                error = 'Not enough stock for: ' + ', '.join(item['product'].name for item in out_of_stock) + '.'

        if error is None:
            total_amount = sum(item['line_total'] for item in items)
            final_amount = total_amount - discount
            bill = Bill.objects.create(
                customer_name=customer,
                total_amount=total_amount,
                discount_amount=discount,
                final_amount=final_amount
            )

            for item in items:
                Billitem.objects.create(
                    bill=bill,
                    product=item['product'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal']
                )
                item['product'].stock -= item['quantity']
                item['product'].save()

            from django.urls import reverse
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(reverse('invoice', args=[bill.id]))

        return render(request, "bill.html", {"products": products, "error": error})

    return render(request, "bill.html", {"products": products})
    

import django.shortcuts

def invoice_view(request, bill_id):
    bill = django.shortcuts.get_object_or_404(Bill, id=bill_id)
    return render(request, 'invoice.html', {'bill': bill})
