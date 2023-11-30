from rest_framework import serializers
from .models import Order, Item


class ItemSerializer(serializers.ModelSerializer):
    price = serializers.CharField(source='stripe.price')
    quantity = serializers.IntegerField(default=1, initial=1)
    tax_rates = serializers.SerializerMethodField('get_tax_rate')

    class Meta:
        model = Item
        fields = ('price', 'quantity', 'tax_rates')

    def get_tax_rate(self, obj):
        if 'order_id' not in self.context:
            return []
        order = Order.objects.get(id=self.context['order_id'])
        tax = order.tax
        tax_rate = [tax.stripe] if tax else []
        return tax_rate


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('items',)

    def get_items(self, obj):
        return ItemSerializer(
            obj.items,
            read_only=True,
            many=True,
            context={'order_id': obj.id}
        ).data
