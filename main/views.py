from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Item, Order, Discount, Tax
from .serializers import OrderSerializer, ItemSerializer
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from decouple import config

stripe.api_key = config('STRIPE_KEY')


# Create your views here.

def item_retrieve(request, id):
    item = get_object_or_404(Item, id=id)
    cart = request.session.get('cart', [])
    cart_items = Item.objects.filter(id__in=cart)
    return render(request, 'item.html', {
        'item': item,
        'cart_items': cart_items,
        'stripe_key': config('STRIPE_PUBLISH_KEY')
    })


def buy_success(request):
    return render(request, 'success.html')


class BuyItemAPIView(APIView):
    def get(self, request, id):
        item = Item.objects.get(id=id)
        line_items = ItemSerializer(item).data
        session = stripe.checkout.Session.create(
            success_url=request.build_absolute_uri(reverse('buy-success')),
            line_items=[line_items],
            currency=item.currency.lower(),
            mode="payment",
        )
        return Response({'id': session['id']})


def add_to_order(request, id):
    cart = request.session.get('cart', [])
    if id not in cart:
        cart.append(id)
    request.session['cart'] = cart
    return JsonResponse({'status': f'{id} added to cart'})


def clear_order(request):
    request.session['cart'] = []
    return JsonResponse({'status': 'cart is cleared'})


class MakeOrderAPIView(APIView):
    def get(self, request):
        # Тут должна быть какая-то логика, по прикреплению скидки к заказу,
        # в данном случаем просто выбирается первый объект из таблицы Discount
        discount = Discount.objects.first()
        cart = request.session.get('cart', [])
        if cart:
            items = Item.objects.filter(id__in=cart)
            order = Order.objects.create()
            order.items.add(*items)
            order.discount = discount
            # Налог так же выбирается - просто первый объект из таблицы Tax
            order.tax = Tax.objects.first()
            order.save()
            line_items = OrderSerializer(order)

            kwargs = {
                'success_url':
                    request.build_absolute_uri(reverse('buy-success')),
                'line_items': line_items.data['items'],
                'currency': 'usd', # По умолчанию валюта для заказов доллары
                'mode': "payment",
            }
            if order.discount:
                kwargs['discounts'] = [{'coupon': order.discount.stripe}]

            session = stripe.checkout.Session.create(**kwargs)
            return Response({'id': session['id']})
        return Response({'error': 'your cart is empty'})
