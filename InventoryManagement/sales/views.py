from django.shortcuts import render, HttpResponse, redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sale, SaleItem, MaterialReport
from e_commerce.models import Order
import json, sys



@login_required
def sales_list(request):
    sales = Sale.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = SaleItem.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'sales/sales.html',context)

@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sale.objects.filter(id=id).first()
    
    if not sales:
        # Handle the case where no sale is found
        messages.error(request, "Sale not found.")
        return redirect('sales:sales-list')

    transaction = {}
    for field in Sale._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales, field.name)
    
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']), '.2f')
    
    ItemList = SaleItem.objects.filter(sale=sales).all()
    context = {
        "transaction": transaction,
        "salesItems": ItemList
    }

    return render(request, 'sales/receipt.html', context)
    # return HttpResponse('')

@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sale.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')

def order_list(request):
    orders = Order.objects.all().order_by("done")
    context = {
        'orders':orders,
    }
    return render(request, 'sales/order_list.html', context)

def mark_orders_as_seen(request):
    # Mark all new orders as seen
    Order.objects.filter(seen_by_user=False).update(seen_by_user=True)
    
    return redirect('sales:order-list')

def order_details(request, pk):
    order = get_object_or_404(Order, pk=pk)
    material_reports = MaterialReport.objects.filter(order= order)
    context = {
        'order':order,
        'material_reports':material_reports,
    }
    return render(request, 'sales/order_details.html', context)