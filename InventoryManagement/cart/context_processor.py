from .cart import Cart
from inventory.models import TAX_RATE, SHIPPING_FEES

def cart_total_amount(request):
    """
    Calculate the total amount of the cart.
    """
    if request.user.is_authenticated:
        cart = Cart(request)
        total_bill = 0.0
        for key, value in request.session.get('cart', {}).items():
            total_bill += float(value['price']) * value['quantity']
        return {'cart_total_amount': total_bill}
    else:
        return {'cart_total_amount': 0.0}

    