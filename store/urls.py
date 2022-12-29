from django.urls import path
from .views import store, cart, checkout, updateItem, processOrder, registerUser, loginUser, logoutUser, detailView

urlpatterns = [
    path('', store, name='store'),
    path('cart', cart, name='cart'),
    path('checkout', checkout, name='checkout'),
    path('update_item', updateItem, name='update_item'),
    path('process_order', processOrder, name='process_order'),
    path('register', registerUser, name="register_user"),
    path('login', loginUser, name='login_user'),
    path('logout', logoutUser, name='logout'),
    path('detail/<int:pk>', detailView, name='detail_view'),
]
