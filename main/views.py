import stripe
from decouple import config
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .blogic import CartManager, StripeSession, OrderCreator
from .models import Item, Discount, Tax
from .serializers import OrderSerializer, ItemSerializer

stripe.api_key = config('STRIPE_KEY')



def item_retrieve(request, id):
    item = get_object_or_404(Item, id=id)
    cart = CartManager.get_cart(request)
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
        item = get_object_or_404(Item, id=id)
        items = ItemSerializer(item).data
        session = StripeSession(request, items, item.currency, 'payment').create()
        return Response({'id': session['id']}, status=status.HTTP_200_OK)


def add_to_order(request, id):
    cart = CartManager.get_cart(request)
    if id not in cart:
        cart.append(id)
    CartManager.set_cart(request, cart)
    return JsonResponse({'detail': f'{id} added to cart'}, status=status.HTTP_200_OK)


def clear_order(request):
    CartManager.clear_cart(request)
    return JsonResponse({'detail': 'cart is cleared'}, status=status.HTTP_200_OK)


class MakeOrderAPIView(APIView):
    def get(self, request):
        # Тут должна быть какая-то логика, по прикреплению скидки и налога к заказу,
        # в данном случаем просто выбирается первый объект из таблицы Discount и Tax
        discount = Discount.objects.first()
        tax = Tax.objects.first()
        cart = CartManager.get_cart(request)
        if cart:
            order = OrderCreator(cart, discount, tax).create()
            items = OrderSerializer(order).data['items']
            session = StripeSession(request, items, 'usd', 'payment', discount).create()
            return Response({'id': session['id']}, status=status.HTTP_200_OK)
        return Response({'detail': 'your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
