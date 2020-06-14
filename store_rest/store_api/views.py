from django.shortcuts import render
from django.db.models import Sum, F, DecimalField
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from .models import User, Product, OrderItem, Order
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer


class UserRegisterAPIView(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for User register
    """
    # The model object to be queried
    queryset = User.objects.all()
    # The serializer to process the data objects
    serializer_class = UserSerializer
    # Allow the request to be processed if there is permission
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for User query
    Implements the following endpoints:
        orders: Returns all orders and respective items made by the user
    """
    # The model object to be queried
    queryset = User.objects.all()
    # The serializer to process the data objects
    serializer_class = UserSerializer

    @action(detail=False)
    def orders(self, request, pk=None):
        """
        Method that implements the 'order' endpoint, returning the orders and respective items
        made by a specific user
        :param request: The request payload
        :param pk: The user ID
        :return: The paginated serialized orders made by this user
        """
        self.pagination_class.page_size = 10
        orders = Order.objects.filter(user_id=pk)
        orders_items = OrderItem.objects.filter(order_id__in=orders)
        page = self.paginate_queryset(orders_items)

        if page is not None:
            serializer = OrderItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderItemSerializer(orders_items, many=True)
        return Response(serializer.data)


class ProductsViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for products.
    Returns the list of products or create a new product to add to the list
    Implements the endpoint 'high_orders' to return a list of products that are part of orders with
    more than 1 product and a total greater than 100.
    """
    # The model object to be queried
    queryset = Product.objects.all()
    # The serializer to process the data objects
    serializer_class = ProductSerializer

    @action(detail=False)
    def high_orders(self, request):
        """
        Method that implement the high_order endpoint, returning a list of products that are part of
        orders with more than 1 product and total value greater than 100
        :param request: The request payload
        :param pk: Not used
        :return: A list of objects that matches the query
        """
        high_orders = Order.objects.annotate(
            total=Sum(
                F('items__quantity') * F('items__product__price'), output_field=DecimalField()
            ).filter(total__gt=100)
        )
        # From the orders, select only those with more than 1 products
        multi_products = high_orders
        products = self.queryset.filter(orderitem__order__in=multi_products)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)


class OrdersViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process request to Orders
    """
    # The model object to perform the queries
    queryset = Order.objects.all()
    # The serializer to process the data objects
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process Order Items
    """
    # the model object to perform the queries
    queryset = OrderItem.objects.all()
    # The serializer to process the data objects
    serializer_class = OrderItemSerializer
