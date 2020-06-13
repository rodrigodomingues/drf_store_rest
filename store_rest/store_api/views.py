from django.db.models import Sum, F, DecimalField
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from .models import User, Product, OrderItem, Order
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer


class UserRegisterAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False)
    def orders(self, request, pk=None):
        self.pagination_class.page_size = 10
        orders = Order.objects.filter(user_id=pk)
        orders_items = OrderItem.objects.filter(order_id__in=orders)
        page = self.paginate_queryset(orders_items)

        if page is not None:
            serializer = OrderItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderItemSerializer(orders_items, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def high_orders(self, request, pk=None):
        # Products where orders are > 100
        high_orders = Order.objects.annotate(
            total=Sum(
                F('items__quantity') * F('items__product__price'), output_field=DecimalField()
            )).filter(total__gt=100)
        products = self.queryset.filter(orderitem__order__in=high_orders)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
