from django.urls import path

from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    UserRegisterAPIView,
    UserViewSet,
    ProductsViewSet,
    OrdersViewSet,
    OrderItemViewSet
)

router = SimpleRouter()

app_name = 'store_api'

urlpatterns = format_suffix_patterns([
    path('register/', UserRegisterAPIView.register_view(), name='register'),
    path('users/', UserViewSet.users_view(), name='users'),
    path('user/<int:pk>', UserViewSet.user_view(), name='user'),
    path('user/<int:pk>/orders', UserViewSet.user_orders_view(), name='user_orders'),

    path('orders/', OrdersViewSet.orders_view(), name='orders'),
    path('orders/create', OrdersViewSet.orders_create_view(), name='orders_create'),
    path('order/<int:pk>', OrdersViewSet.order_view(), name='order'),

    path('order_items/', OrderItemViewSet.order_items_view(), name='order_items'),
    path('order_item/<int:pk>', OrderItemViewSet.order_item_view(), name='order_item'),

    path('products/', ProductsViewSet.products_view(), name='products'),
    path('products/create', ProductsViewSet.product_create_view(), name='products_create'),
    path('product/<int:pk>', ProductsViewSet.product_view(), name='product'),
    path('products/high_orders', ProductsViewSet.product_high_orders_view(), name='high_orders')
])

urlpatterns += router.urls

