from django.shortcuts import render, HttpResponse,get_object_or_404, redirect
from django.contrib import messages
from inventory.models import Stock
from django.contrib.auth.decorators import login_required
import json, sys
from datetime import date, datetime
from sales.models import Sale, SaleItem, MaterialReport
from .models import Outbound, OutboundItem
from django.utils import timezone
from .utils import process_outbound,process_inbound 
from django.http import JsonResponse
from inventory.models import TAX_RATE
from django.db import IntegrityError
from e_commerce.models import Order, OrderItem

# To Do List 
# Work On the Inbound First, To determine a specific quantity for each product 
# Then recover The reporting system we had in the previous project is_expiring_soon, Low_in_stock
# Work On the outbound and link it to the sales
#  29/10/2024 Almost Done 

@login_required
def pos(request):
    products = Stock.objects.filter(active = True)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.unit_cost)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json),
        'tax_rate':TAX_RATE,
    }
    # return HttpResponse('')
    return render(request, 'pos/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'pos/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status': 'failed', 'msg': ''}
    data = request.POST

    # Debug: Log incoming data
    print("Incoming POST data:", data)

    # Generate unique sale code based on the current year
    pref = datetime.now().year * 10000  # Ensure unique prefix
    sale_code = generate_unique_code(Sale, pref)
    out_code = generate_unique_code(Outbound, pref)

    try:
        # Loop through products and save SaleItems
        for i, product_id in enumerate(data.getlist('product_id[]')):
            qty = int(data.getlist('qty[]')[i])  # Convert quantity to int
            price = float(data.getlist('price[]')[i])  # Convert price to float
            total = qty * price

            product = Stock.objects.filter(id=product_id).first()
            if product:  # Ensure product exists

                # Process outbound
                var = process_outbound(product, qty)
                if 'quantity cannot be processed' == var:
                    messages.warning(request, var)
                elif 'Null values are passed, track your process!' == var:
                    messages.warning(request, var)
                elif "Outbound processing completed successfully." == var:
                    # Create Sale instance
                    sales = Sale(
                        code=sale_code,
                        sub_total=float(data['sub_total']),
                        tax=float(data['tax']),
                        tax_amount=float(data['tax_amount']),
                        grand_total=float(data['grand_total']),
                    )
                    sales.save()

                    # Create Outbound instance
                    outbound = Outbound(
                        code=out_code,
                        responsible_staff=request.user,
                        sale=sales,
                    )
                    outbound.save()
                    SaleItem.objects.create(
                    sale=sales,
                    item=product,
                    qty=qty,
                    price=price,
                    total=total
                    )
                    OutboundItem.objects.create(
                        material=product,
                        outbound=outbound,
                        quantity=qty,
                        total_price=total,
                        sold_date=timezone.now()
                    )
                    product.save()

            else:
                var = f"Product with id {product_id} not found."
                print(var)
                messages.warning(request, var)

        resp['status'] = 'success'
        resp['sale_id'] = sales.pk  # Use the primary key from the created instance
        messages.success(request, "Sale Record has been saved.")


    except Exception as e:
        resp['msg'] = "An error occurred: " # when quantity > availability 
        print("Unexpected error:", e)
        messages.error(request, resp['msg'])

    return JsonResponse(resp)

def generate_unique_code(model, prefix):
    """ Generate a unique code for the given model based on a prefix. """
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        check = model.objects.filter(code=f"{prefix}{code}").exists()
        if not check:
            return f"{prefix}{code}"
        i += 1



def inbound(request):
    if request.method == 'POST':
        try:
            # Extract product details from the POST request
            product_ids = request.POST.getlist('product_id[]')
            quantities = request.POST.getlist('qty[]')
            expiration_dates = request.POST.getlist('expiry[]')
            source = request.POST.get('source')
            
            if not product_ids or not quantities or not expiration_dates:
                raise ValueError("Missing product details.")
            
            # Prepare products for processing
            products = [(product_id, qty, expiry) for product_id, qty, expiry in zip(product_ids, quantities, expiration_dates)]
            
            # Call the process_inbound function
            result_message = process_inbound(request.user, products, source)
            
            # Display success message
            messages.success(request, result_message)
            return redirect('inventory:product')  # Redirect to a different page after success

        except ValueError as e:
            # Handle invalid data (e.g., missing product details)
            messages.error(request, f"Error: {str(e)}")
            return redirect('inventory:inbound')  # Stay on the current page if error occurs
        except IntegrityError as e:
            # Handle database errors (e.g., unique constraint violation, foreign key error)
            messages.error(request, f"Database error: {str(e)}")
            return redirect('inventory:inbound')
        except Exception as e:
            # Catch unexpected errors and inform the user
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect('inventory:inbound')

    else:
        # Handle GET requests: prepare product list for the user
        try:
            products = Stock.objects.filter(active=True)
            product_json = [{'id': product.id, 'name': product.name} for product in products]
            context = {
                'page_title': "Inbound",
                'products': products,
                'product_json': json.dumps(product_json),
            }
            return render(request, 'pos/inbound.html', context)
        except Exception as e:
            # Handle errors when fetching product data
            messages.error(request, f"Error loading product list: {str(e)}")
            return redirect('inventory:product')



def saleorder(request, pk):
    # Fetch the order and its items
    order = get_object_or_404(Order, id=pk)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, 'pos/saleorder.html', context)


def confirm_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    order_items = OrderItem.objects.filter(order=order)

    # Generate unique codes for Sale and Outbound
    prefix = datetime.now().year * 10000  # Ensure a unique prefix for codes
    sale_code = generate_unique_code(Sale, prefix)
    outbound_code = generate_unique_code(Outbound, prefix)

    try:
        # Create the Sale record
        sale = Sale(
            user=order.user,
            code=sale_code,
            order=order,
            sub_total=order.subtotal,
            grand_total=order.total,
            tax_amount=order.tax,
        )
        sale.save()

        # Mark the order as completed
        order.done = True
        order.save()

        # Create the Outbound record
        outbound = Outbound(
            code=outbound_code,
            responsible_staff=request.user,
            sale=sale,
        )
        outbound.save()

        # Process each item in the order
        for item in order_items:
            quantity = int(item.quantity)
            price = float(item.price)
            total = float(item.total)

            # Fetch the corresponding product from Stock
            product = Stock.objects.filter(id=item.product.id).first()
            if product:
                # Attempt to process the outbound operation
                process_status = process_outbound(product, quantity)
                if process_status == 'quantity cannot be processed':
                    messages.warning(request, process_status)
                elif process_status == 'Null values are passed, track your process!':
                    messages.warning(request, process_status)
                elif process_status == "Outbound processing completed successfully.":
                    # Create SaleItem and OutboundItem records
                    SaleItem.objects.create(
                        sale=sale,
                        item=product,
                        qty=quantity,
                        price=price,
                        total=total
                    )
                    OutboundItem.objects.create(
                        material=product,
                        outbound=outbound,
                        quantity=quantity,
                        total_price=total,
                        sold_date=timezone.now()
                    )
                    # Save product changes
                    product.save()
            else:
                # Handle missing product
                message = f"Product {item.product.name} not found."
                print(message)
                messages.warning(request, message)

        # Add a success flash message
        messages.success(request, f"Sale record for order {order.id} has been saved successfully.")

    except Exception as e:
        # Handle unexpected errors and add an error flash message
        print(f"Unexpected error: {e}")
        messages.error(request, "An error occurred during the sale process. Please try again.")

    # Redirect to the sales order list
    return redirect('pos:pos')

