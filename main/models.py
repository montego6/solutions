from django.db import models
from django.urls import reverse
import stripe
from decouple import config

stripe.api_key = config('STRIPE_KEY')


class Item(models.Model):
    class Currency(models.TextChoices):
        usd = 'usd', 'American Dollar'
        eur = 'eur', 'Euro'
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    currency = models.CharField(max_length=200, choices=Currency.choices, default=Currency.usd)

    def save(self, *args, **kwargs):
        product = stripe.Product.create(name=self.name)
        if self.currency.lower() == 'usd':
            currency_options = \
                {'eur': {'unit_amount': int(self.price * 0.93 * 100)}}
        elif self.currency.lower() == 'eur':
            currency_options = \
                {'usd': {'unit_amount': int(self.price * 1.07 * 100)}}
        else:
            currency_options = {}

        price = stripe.Price.create(
            unit_amount=int(self.price * 100),
            currency=self.currency,
            product=product['id'],
            currency_options=currency_options,
        )

        # Если модель обновляется, то удаляем связанный stripe объект
        if not self._state.adding:
            self.stripe.delete()
        super().save(*args, **kwargs)
        StripeItem.objects.create(
            item=self,
            product=product['id'],
            price=price['id']
        )

    def __str__(self):
        return f'{self.id} - {self.name} - {self.price}'

    def get_buy_url(self):
        return reverse('buy-item', kwargs={'id': self.id})

    def add_to_order_url(self):
        return reverse('add-to-order', kwargs={'id': self.id})


# Модель для связывания с Item
class StripeItem(models.Model):
    item = models.OneToOneField(
        Item,
        on_delete=models.CASCADE,
        related_name='stripe'
    )
    product = models.CharField(max_length=300)
    price = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.item.name} - {self.item.price}'


class Order(models.Model):
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(
        'Discount',
        on_delete=models.SET_NULL,
        null=True
    )
    tax = models.ForeignKey('Tax', on_delete=models.SET_NULL, null=True)


class Discount(models.Model):
    discount = models.FloatField()
    stripe = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        coupon = stripe.Coupon.create(percent_off=self.discount)
        self.stripe = coupon['id']
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.discount}'


class Tax(models.Model):
    name = models.CharField(max_length=300)
    inclusive = models.BooleanField()
    percentage = models.FloatField()
    stripe = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        tax_rate = stripe.TaxRate.create(
            display_name=self.name,
            inclusive=self.inclusive,
            percentage=self.percentage
        )
        self.stripe = tax_rate['id']
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.percentage}'
