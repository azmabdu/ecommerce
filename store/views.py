from django.shortcuts import render
from django.http.response import JsonResponse
import json
from datetime import datetime
from .models import Product, ShippingAddress, Order, OrderItem, Customer


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    return render(request, 'store/store.html', {'products': products, 'cartItems': cartItems})


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    return render(request, 'store/cart.html', {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False})


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
        cartItems = order['get_cart_items']

    return render(request, 'store/checkout.html', {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False})


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('ID:', productId, 'Action:', action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse(f'Update:{action}', safe=False)


def processOrder(request):
    data = json.loads(request.body)
    transaction_id = datetime.now().timestamp()
    print(transaction_id)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True

        order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    else:
        print('Not logged in')

    return JsonResponse('Payment Submitted...', safe=False)
