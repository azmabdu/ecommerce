from django.contrib import admin
from .models import Customer, Order, OrderItem, ShippingAddress, Product

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Product)
