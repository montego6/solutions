import stripe

class CartManager:
    @staticmethod
    def get_cart(request):
        return request.session.get('cart', [])
    @staticmethod
    def clear_cart(request):
        request.session['cart'] = []


class StripeSession:
    def __init__(self, request, items, currency, mode) -> None:
        self.request = request
        self.items = items
        self.currency = currency
        self.mode = mode

    def create(self):
        return stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse('buy-success')),
            line_items=[line_items],
            currency=item.currency,
            mode="payment",
        )