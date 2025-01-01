from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from inventory.models import Contact_us, Color, Category, Stock, SHIPPING_FEES, TAX_RATE
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from decimal import Decimal
from e_commerce.models import Order, OrderItem
from django.contrib import messages 
from sales.models import MaterialReport
from pos.models import InboundItem

# Complete Place order Part To link this app properly to the project
def ABOUT(request):
    return render(request,'main/about.html')


def base(request):
    return render(request, 'main/base.html')

def Home(request):
    product = Stock.objects.all()
    context = {
        'product':product,
    }
    return render(request,'main/index.html',context)


def SEARCH(request):
    query = request.GET.get('query')
    product = Stock.objects.filter(name__icontains=query)
    context = {
        'product': product
    }
    return render(request, 'main/search.html', context)

@login_required(login_url="e_commerce:login")
def PRODUCT_DETAILS_PAGE(request,id):
    prod = get_object_or_404(Stock, id=id)
    context = {
        'prod': prod
    }
    return render(request, 'main/product_single.html',context)


@login_required(login_url="e_commerce:login")
def PRODUCT(request):
    # Default product list
    product = Stock.objects.filter(active=True)
    mhm = "Default"  # Default label

    # Handling sorting
    if 'ATOZ' in request.GET:
        product = product.order_by('name')
        mhm = "A to Z"
    elif 'ZTOA' in request.GET:
        product = product.order_by('-name')
        mhm = "Z to A"
    elif 'NTOD' in request.GET:
        product = product.order_by('-id')  # Assuming 'id' is creation date or similar
        mhm = "New"
    elif 'DTON' in request.GET:
        product = product.order_by('id')  # Oldest first
        mhm = "Old"

    # Fetch categories and colors
    categories = Category.objects.all()
    product_colors = Color.objects.all()

    # Pass context to the template
    context = {
        "mhm": mhm,
        "product_colors": product_colors,
        "categories": categories,
        "product": product,
    }

    return render(request, 'main/product.html', context)

def CONTACT_US(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        contact = Contact_us(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        # Define the email subject, message, and sender
        email_subject = subject
        email_message = f"From: {name} <{email}>\n\nMessage:\n{message}"
        email_from = settings.EMAIL_HOST_USER

        try:
            # Send the email
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=email_from,
                recipient_list=['Hammodehyaser79@gmail.com'],  
                fail_silently=False,
            )
            contact.save()  # Save to the database if email was sent successfully
            return redirect('e_commerce:home')
        
        except Exception as e:
            print(f"Error sending email: {e}")  # For debugging
            return redirect('e_commerce:contact')
    return render(request,'main/contact.html')

def HandleRegister(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        customer = User.objects.create_user(username,email,pass1)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()
        return redirect('e_commerce:home')
    return render(request,'main/registration/auth.html')

def HandleLogin(request):
     if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('e_commerce:home')
        else:
            return redirect('e_commerce:login')
     return render(request,'main/registration/auth.html')

def HandleLogout(request):
    logout(request)
    return redirect('e_commerce:home')

@login_required(login_url="e_commerce:login")
def cart_add(request, id):
    cart = Cart(request)
    product = Stock.objects.get(id=id)
    cart.add(product=product)
    return redirect("e_commerce:product")


@login_required(login_url="e_commerce:login")
def item_clear(request, id):
    cart = Cart(request)
    product = Stock.objects.get(id=id)
    cart.remove(product)
    return redirect("e_commerce:cart_detail")


@login_required(login_url="e_commerce:login")
def item_increment(request, id):
    cart = Cart(request)
    product = Stock.objects.get(id=id)
    cart.add(product=product)
    return redirect("e_commerce:cart_detail")


@login_required(login_url="e_commerce:login")
def item_decrement(request, id):
    cart = Cart(request)
    product = Stock.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("e_commerce:cart_detail")


@login_required(login_url="e_commerce:login")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()

    return redirect("e_commerce:cart_detail")


@login_required(login_url="e_commerce:login")
def cart_detail(request):
    context = {
        'user':request.user,
        'shipping_fees':SHIPPING_FEES,
        'tax_rate':TAX_RATE
    }
    return render(request, 'cart/cart_details.html', context)

def generate_order_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    pdf = order.generate_pdf()
    
    if pdf is None:
        return HttpResponse("Error generating PDF", status=500)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_requisition_{pk}.pdf"'
    return response

def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk = pk)

    context = {
        'order':order,
    }
    return render(request, 'bills/order_confirmation.html', context)

@login_required(login_url="e_commerce:login")
def Check_out(request):
    if request.method == 'POST':
        pass
    user = request.user

    context = {
        'user':user,
        'shipping_fees':SHIPPING_FEES,
        'tax_rate':TAX_RATE
    }
    return render(request, 'cart/checkout.html', context)

@login_required(login_url="e_commerce:login")
def PLACE_ORDER(request):
    
    if request.method=="POST":
        # Retrieve the order data from the POST request
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        country=request.POST.get('country')
        city=request.POST.get('city')
        address=request.POST.get('address')
        postcode=request.POST.get('postcode')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        additional_info=request.POST.get('additional_info')

        # Ensure all required fields are filled
        if firstname and lastname and country and address and postcode and phone and email:
            # Create the Order object
            order = Order(
                user=request.user,
                firstname=firstname,
                lastname=lastname,
                contry=country,
                city=city,
                address=address,
                postcode=postcode,
                phone=phone,
                email=email,
                additional_info=additional_info,
            )
            order.save()  # Save the order to the database

            cart = Cart(request)  # Instantiate the Cart class to access cart items
            cart_items = cart.cart  # Get the cart items

            # Calculate the cart total, tax, shipping, etc.
            cart_total = Decimal('0.00')  # Initialize cart total as Decimal
            for item in cart_items.values():
                cart_total += Decimal(item['price']) * Decimal(item['quantity'])  # Calculate the item total
                # Create an OrderItem for each product in the cart
                product = get_object_or_404(Stock, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],

                )
                quantity = float(item['quantity'])
                inbound_items = InboundItem.objects.filter(material=product, active = True).order_by('expiration_date')
                for item in inbound_items:
                    if item.quantity <= 0:
                        continue  # Skip items with zero quantity

                    # Process the outbound quantity
                    if quantity > 0:
                        if item.quantity >= quantity:
                            item.quantity -= quantity
                            print(f"Processed {quantity} from {item.material.name}. Remaining quantity: {item.quantity}")
                            
                            MaterialReport.objects.create(
                                material = product,
                                quantity = quantity,
                                order = order,
                                
                                expiration_date=item.expiration_date,
                                )
                            quantity = 0  # All quantity has been processed
                            break
                            
                        else:
                            quantity -= item.quantity
                            MaterialReport.objects.create(
                                material = product,
                                quantity = item.quantity,
                                order = order,
                                location = item.location,
                                expiration_date=item.expiration_date,
                            )
                            print(f"Processed {item.quantity} from {item.material.name}. Remaining quantity to process: {quantity}")
                            item.quantity = 0  # All of this item is consumed
                    else:
                        break  # No quantity left to process

                if quantity > 0:
                    message = f"Not all of the requested quantity for {product.name} could be processed."
                    print(message)

            # Calculate additional costs (shipping, tax, etc.)
            tax = float(cart_total) * TAX_RATE
            total_amount = float(cart_total) + SHIPPING_FEES + tax  # Final total amount including tax and shipping

            # Optionally, you can also update the order with the final amount
            order.amount = str(total_amount)
            order.save()  # Save the updated order with the total amount

            # Clear the cart after placing the order
            cart.clear()

            # Show a success message
            messages.success(request, 'Your Order Has Been Successfully Created!')

            # Redirect to a confirmation page or render the confirmation page with relevant context
            context = {
                'order': order,
                'cart_total': cart_total,
                'tax': tax,
                'shipping_cost': SHIPPING_FEES,
                'total_amount': total_amount,
            }

            return render(request, 'cart/placeorder.html', context)
        else: 
            messages.warning(request, 'Please fill in all required fields.')
            return redirect('e_commerce:checkout')
    
    # If it's a GET request, render the order page with the initial context
    context = {
        'tax': TAX_RATE,
        'shipping_cost': SHIPPING_FEES,
    }
    
    return render(request, 'cart/placeorder.html', context)

def billing(request, pk):
    order = get_object_or_404(Order, pk = pk)
    order_items = OrderItem.objects.filter(order = order)
    context = {
        'order':order,
        'order_items':order_items
    }

    return render(request, 'cart/Billing.html',context)
