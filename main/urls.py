from django.urls import path
from . import views

urlpatterns = [
    path('item/<int:id>/', views.item_retrieve, name='item-retrieve'),
    path('item/<int:id>/add-to-order',
         views.add_to_order,
         name='add-to-order'),
    path('buy/<int:id>/', views.BuyItemAPIView.as_view(), name='buy-item'),
    path('buy/order/', views.MakeOrderAPIView.as_view(), name='make-order'),
    path('buy/order/clear/', views.clear_order, name='clear-order'),
    path('buy/success/', views.buy_success, name='buy-success'),
]
