from django.urls import path

from rest_framework.routers import SimpleRouter

from .views import (
    UserRegisterAPIView,
    UserViewSet,
    ProductsViewSet,
    OrdersViewSet,
    OrderItemViewSet
)


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view({
        'post': 'create'
        },
        name='register'
    )),
    path('users/', UserViewSet.as_view(
        {
            'get': 'list'
        },
        name='users'
    )),
    path('user/<int:pk>', UserViewSet.as_view(
        {
            'get': 'retrieve',
            'put': 'update'
        },
        name='user'
    )),
    path('user/<int:pk>/orders', UserViewSet.as_view(
        {
            'get': 'orders'
        },
        name='user_orders'
    )),

    path('orders/', OrdersViewSet.as_view(
        {
            'get': 'list'
        },
        name='orders'
    )),
    path('orders/create', OrdersViewSet.as_view(
        {
            'post': 'create'
        },
        name='orders_create'
    )),
    path('order/<int:pk>', OrdersViewSet.as_view(
        {
            'get': 'retrieve',
            'put': 'update'
        },
        name='order'
    )),

    path('order_items/',OrderItemViewSet.as_view({
        'get': 'list',
        'post': 'create'
        },
        name='order_items')),
    path('order_item/<int:pk>', OrderItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
        },
        name='order_item')),

    path('products/', ProductsViewSet.as_view({
        'get': 'list'
        },
        name='products'
    )),
    path('products/create', ProductsViewSet.as_view({
        'post': 'create'
        },
        name='products_create')),
    path('product/<int:pk>', ProductsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
        },
        name='product')),
    path('product/high_orders', ProductsViewSet.as_view({
        'get': 'high_orders',
        },
        name='product_high_order'))
]



