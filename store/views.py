from django.shortcuts import render, redirect
from django.http.response import JsonResponse
import json
from datetime import datetime
from .models import Product, ShippingAddress, Order, OrderItem, Customer
from django.views.decorators.csrf import csrf_exempt
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def getCartItems(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']
    return cartItems


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


@login_required(login_url='/login')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    return render(request, 'store/cart.html', {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False})


@csrf_exempt
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


def registerUser(request):
    cartItems = getCartItems(request)
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            user = form.save()
            # create customer
            customer = Customer.objects.create(
                user=user,
                email=email,
                name=username,
            )
            customer.save()
            messages.success(request, f'{user} has been created')
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Error occured')
    form = UserForm()
    return render(request, 'store/register.html', {'form': form, 'cartItems': cartItems})


def loginUser(request):
    cartItems = getCartItems(request)
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        else:
            messages.error(request, 'No account with these credentials')
    form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form, 'cartItems': cartItems})


def logoutUser(request):
    logout(request)
    return redirect('store')


def detailView(request, pk):
    cartItems = getCartItems(request)
    product = Product.objects.get(pk=pk)
    return render(request, 'store/detail.html', {'product': product})
