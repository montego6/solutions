import stripe
from django.urls import reverse

class CartManager:
    @staticmethod
    def get_cart(request):
        return request.session.get('cart', [])
    @staticmethod
    def clear_cart(request):
        request.session['cart'] = []
    @staticmethod
    def set_cart(request, cart):
        request.session['cart'] = cart


class StripeSession:
    def __init__(self, request, items, currency, mode) -> None:
        self.request = request
        self.items = items if isinstance(items, list) else [items]
        self.currency = currency
        self.mode = mode

    def create(self):
        return stripe.checkout.Session.create(
            success_url=self.request.build_absolute_uri(reverse('buy-success')),
            line_items=self.items,
            currency=self.currency,
            mode=self.mode,
        )
    

class OrderCreator:
    def __init__(self, cart, discount, tax):
        self.cart = cart
        self.discount = discount
        self.tax = tax