from django.shortcuts import render,redirect,get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime
from django.contrib.auth.models import User
from django.db.models import F, Sum
from .utils import generate_rgba_colors, fetch_top_stocks, prepare_inventory_data, top_10_stocks_chart, generate_charts, create_location_until_available
from inventory.models import Category, Stock, Color, InventoryLocation, Inventory
from sales.models import Sale
import json, sys
from django.contrib import messages
from .forms import CreateStockForm, UpdateStockForm
from pos.models import InboundItem, OutboundItem
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from e_commerce.models import Order

# To Do List 
# Separate Manage Category into Create - Update
# Separate Manage Product into Create - Update
# Create a Dashboard View and add Some charts using plotly
# Recreate A product page For further Analysis

@login_required(login_url='user:user-login')
def index(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Stock.objects.all())
    transaction = len(Sale.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sale.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total',flat=True))
    
    # Fetch reports and stocks
    low_stock_items = Stock.objects.filter(stocks_availability__lt=F('threshold')).order_by('stocks_availability')

    # Exp-date
    expiring_soon_threshold = 30  
    expiring_items = InboundItem.objects.filter(
        expiration_date__lte=date.today() + timedelta(days=expiring_soon_threshold),
        active=True
    ).values('material__name', 'expiration_date').annotate(total_quantity=Sum('quantity')).order_by('expiration_date')

    # This will give you a queryset with unique (material name, expiration date) pairs and their total quantities  

    # Charts
    orders = Order.objects.all()
    order_labels=[]
    order_data = []
    for order in orders:
        order_labels.append(f'ORDER_{order.id}')
        order_data.append(sum(float(item.quantity) for item in order.orderitem_set.all()))
    
    products_freq = Stock.objects.all()
    pie_chart_html, bar_chart_html = generate_charts(order_labels, order_data, products_freq)


    context = {
        'low_stock_items':low_stock_items,
        'expiring_items':expiring_items,
        'bar_chart_html':bar_chart_html,
        'pie_chart_html':pie_chart_html,
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
    }
    return render(request, 'inventory/home.html',context)

@login_required(login_url='user:user-login')
def inventory(request):
    context = prepare_inventory_data()
    return render(request, 'partials/inventory.html', context)

@login_required(login_url='user:user-login')
def show_inventory_layout(request, pk, row_id=None):
    inventory = get_object_or_404(Inventory, id=pk)

    if row_id:
        columns = []
        for column_num in range(1, inventory.columns_number + 1):
            total_layers = inventory.layers_number
            reserved_layers = InventoryLocation.objects.filter(
                inventory=inventory, row=row_id, column=column_num, reserved=True
            ).count()
            available_layers = total_layers - reserved_layers
            columns.append({
                'column': column_num,
                'empty_spaces': available_layers
            })

        locations = InventoryLocation.objects.filter(
            inventory=inventory, row=row_id
        ).order_by('column', 'layer')

        return render(request, 'partials/row.html', {
            'inventory': inventory,
            'row_id': row_id,
            'columns': columns,
            'locations': locations
        })

    rows = []
    for row_num in range(1, inventory.rows_number + 1):
        total_spaces = inventory.columns_number * inventory.layers_number
        reserved_spaces = InventoryLocation.objects.filter(
            inventory=inventory, row=row_num, reserved=True
        ).count()
        available_spaces = total_spaces - reserved_spaces
        rows.append({
            'row': row_num,
            'empty_spaces': available_spaces
        })

    return render(request, 'partials/row.html', {
        'inventory': inventory,
        'rows': rows
    })

@login_required(login_url='user:user-login')
def show_column_layout(request, pk, row_id, column_id):
    inventory = get_object_or_404(Inventory, id=pk)

    layers = []
    for layer_id in range(1, inventory.layers_number + 1):
        reserved_layer = InventoryLocation.objects.filter(
            inventory=inventory, row=row_id, column=column_id, layer=layer_id, reserved=True
        ).count()
        available_layer = 1 - reserved_layer

        # Fetch the stock associated with this layer, if any
        location = InventoryLocation.objects.filter(
            inventory=inventory, row=row_id, column=column_id, layer=layer_id, reserved=True
        ).first()
        stock_name = location.stock.material.name if location and location.stock else None
        stock_q = location.stock.quantity if location and location.stock else None
        layers.append({
            'layer_id': layer_id,
            'available_layer': available_layer,
            'stock_id': stock_name,
            'stock_q': stock_q,
        })
    
    layers = list(reversed(layers))
    locations = InventoryLocation.objects.filter(
        inventory=inventory, row=row_id, column=column_id
    ).order_by('layer')

    return render(request, 'partials/column.html', {
        'inventory': inventory,
        'row_id': row_id,
        'column_id': column_id,
        'layers': layers,
        'locations': locations,

    })

@login_required(login_url='user:user-login')
@require_POST
def report_stock_issue(request):
    issue_type = request.POST.get('issue_type')  # 'low_stock' or 'expiry'
    items = request.POST.getlist('items')  # List of item IDs

    if not items:
        return JsonResponse({'status': 'error', 'message': 'No items selected.'}, status=400)

    if issue_type == 'low_stock':
        subject = 'Low Stock Report'
        item_list = ", ".join(items)  # Join IDs for clarity
        message = f'The following items are low in stock: {item_list}'
    elif issue_type == 'expiry':
        subject = 'Expiration Date Report'
        item_list = ", ".join(items)  # Join IDs for clarity
        message = f'The following items are nearing expiration: {item_list}'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid issue type.'}, status=400)

    # Send email
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  # Ensure ADMIN_EMAIL is set in your settings
            fail_silently=False,
        )
        return JsonResponse({'status': 'success', 'message': 'Report submitted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error sending email: {str(e)}'}, status=500)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'pos/about.html',context)

#Categories
@login_required(login_url='user:user-login')
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'inventory/category.html',context)

@login_required(login_url='user:user-login')
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'inventory/manage_category.html',context)

@login_required(login_url='user:user-login')
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'])
        else:
            save_category = Category(name=data['name'], description = data['description'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required(login_url='user:user-login')
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required(login_url='user:user-login')
def product(request):
    product_list = Stock.objects.all().order_by('category')
    categories = Category.objects.all().order_by('name')
    context = top_10_stocks_chart()
    context['page_title'] = 'Product List'
    context[ 'products'] =product_list
    context['categories'] = categories
    return render(request, 'inventory/products.html',context)

@login_required(login_url='user:user-login')
def prodcut_page(request, pk):
    stock = get_object_or_404(Stock, id=pk)
    in_items = InboundItem.objects.filter(material = stock, active=True)
    out_items = OutboundItem.objects.filter(material = stock)
    product_colors = Color.objects.all() 
    revenue_data = [0] * 12
    sales_frequency_data = [0] * 12
    for item in out_items:
        month = item.sold_date.month - 1  # Zero-indexed month
        revenue_data[month] += item.material.unit_cost * item.quantity
        sales_frequency_data[month] += item.quantity

    context = {
        'product_colors':product_colors,
        'stock': stock,
        'in_items': in_items,
        'revenue_data': revenue_data,
        'sales_frequency_data':sales_frequency_data,
    }
    return render(request, 'inventory/product_page.html', context)


from django.core.exceptions import ValidationError

@login_required(login_url='user:user-login')
def manage_product(request):
    if request.method == "POST":
        form = CreateStockForm(request.POST, request.FILES)
        # Handling Stock creation and assignment
        if form.is_valid():
            stock = form.save()
            try:
                # Try to assign the location using the available location creation function
                location = create_location_until_available(stock.inventory.id)
                stock.location = location
                stock.save()  # Save the stock with the location
            except ValueError as e:
                # If the function fails to assign a location, delete the stock to prevent errors
                stock.delete()
                raise ValidationError(str(e))  # Raise a validation error with the error message

            stock_name = form.cleaned_data.get('name')
            messages.success(request, f'{stock_name} has been successfully added.')
            return redirect('inventory:product')
        else:
            messages.warning(request, 'Form is not valid. Please correct the errors below.')
    else:
        form = CreateStockForm()

    return render(request, 'inventory/manage_product.html', {'form': form})

@login_required(login_url='user:user-login')
def update_product(request , pk):
    stock = get_object_or_404(Stock, id = pk)
    if request.method == 'POST':
        form = UpdateStockForm(request.POST, request.FILES, instance=stock)
        if form.is_valid():
            form.save()
            stock_name = form.cleaned_data.get('name')
            messages.success(request, f'{stock_name} has been successfully Updated.')
            return redirect('inventory:product')
        else:
            form = UpdateStockForm(instance=stock)
            messages.warning(request, 'Form is not valid. Please correct the errors below.')
            return render(request, 'inventory/update_product.html', {'form': form})
    else:
        form = UpdateStockForm(instance=stock)
        return render(request, 'inventory/update_product.html',{'form':form, 'stock':stock})

@login_required(login_url='user:user-login')
def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'inventory/test.html',context)

@login_required(login_url='user:user-login')
def save_product(request):
    data =  request.POST
    resp = {'status':'failed'}
    id= ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Stock.objects.exclude(id=id).filter(vocab_no=data['code']).all()
    else:
        check = Stock.objects.filter(vocab_no=data['code']).all()
    if len(check) > 0 :
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_product = Stock.objects.filter(id = data['id']).update(vocab_no=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
            else:
                save_product = Stock(vocab_no=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),status = data['status'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required(login_url='user:user-login')
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Stock.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
