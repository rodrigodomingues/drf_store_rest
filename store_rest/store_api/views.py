from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from .models import User, Product, OrderItem, Order
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer


class UserRegisterAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny, )


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
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


class ProductViewSet(mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductsViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'])
    def high_orders(self, request, pk=None):
        pass


class OrdersViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderViewSet(mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
