from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    UserRegisterAPIView,
    UserViewSet,
    ProductsViewSet,
    OrdersViewSet,
    OrderItemViewSet
)

router = SimpleRouter()

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view({
        'post': 'create'
    })),

    path('users/', UserViewSet.as_view({
        'get': 'list'
    })),
    path('user/<int:pk>', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('user/<int:pk>/orders', UserViewSet.as_view({
        'get': 'orders'
    })),

    path('orders/', OrdersViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('order/<int:pk>', OrdersViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),

    path('order_items/', OrderItemViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),

    path('order_item/<int:pk>', OrderItemViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),

    path('products/', ProductsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('product/<int:pk>', ProductsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('product/<int:pk>/high_orders', ProductsViewSet.as_view({
        'get': 'high_orders',
    })),
]

urlpatterns += router.urls
