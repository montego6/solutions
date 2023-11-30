import stripe
from django.urls import reverse
from .models import Item, Order

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
    def __init__(self, request, items, currency, mode, discount=False) -> None:
        self.request = request
        self.items = items if isinstance(items, list) else [items]
        self.currency = currency
        self.mode = mode
        self.discount = discount

    def create(self):
        discount = {
                'discounts': [{'coupon': self.discount.stripe}]
            } if self.discount else {}
        
        return stripe.checkout.Session.create(
            success_url=self.request.build_absolute_uri(reverse('buy-success')),
            line_items=self.items,
            currency=self.currency,
            mode=self.mode,
            **discount
        )
    

class OrderCreator:
    def __init__(self, cart, discount, tax):
        self.cart = cart
        self.discount = discount
        self.tax = tax

    def create(self):
        items = Item.objects.filter(id__in=self.cart)
        order = Order.objects.create(tax=self.tax, discount=self.discount)
        order.items.add(*items)
        return order