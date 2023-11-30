from django.contrib import admin
from .models import Item, StripeItem, Order, Discount, Tax

admin.site.register(Item)
admin.site.register(StripeItem)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(Tax)
# Register your models here.
