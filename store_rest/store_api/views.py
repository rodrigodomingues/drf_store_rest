import logging

from django.shortcuts import render
from django.db.models import Sum, F, Q, DecimalField
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import PermissionDenied

from rest_framework.response import Response
from rest_framework import permissions, status
from .models import User, Product, OrderItem, Order
from .permissions import IsOwner
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer


class UserRegisterAPIView(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for User register

    Provides the following view routes and methods
        register_view (post - create)

    This is splitted from the other user viewset class due to allowing the operation without permissions
    """
    # The model object to be queried
    queryset = User.objects.all()
    # The serializer to process the data objects
    serializer_class = UserSerializer
    # Allow the request to be processed if there is permission
    permission_classes = (permissions.AllowAny,)

    @classmethod
    def register_view(cls):
        return cls.as_view(
            {
                'post': 'create'
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for User query

    Provides the following view routes and methods:
        users_view (get - list)
        user_view  (get - detail, put - update)
        users_order_view (get - detail)

    Implements the following endpoints:
        orders (get): Returns all orders and respective items made by the user
    """
    # The model object to be queried
    queryset = User.objects.all()
    # The serializer to process the data objects
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False)
    def orders(self, request, pk=None):
        """
        Method that implements the 'order' endpoint, returning the orders and respective items
        made by a specific user
        :param request: The request payload
        :param pk: The user ID
        :return: The paginated serialized orders made by this user
        """
        # A simple validation (it seems for this method the validation classes are not being applied!)
        if request.user.id != pk and not request.user.is_staff:
            raise PermissionDenied('User not authorized to perform this operation', status.HTTP_403_FORBIDDEN)
        self.pagination_class.page_size = 10
        orders = Order.objects.filter(user_id=pk)
        orders_items = OrderItem.objects.filter(order_id__in=orders)
        page = self.paginate_queryset(orders)

        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    """
        Specifies the userviews to be informed in the routes
    """

    @classmethod
    def users_view(cls):
        return cls.as_view({
            'get': 'list'
        })

    @classmethod
    def user_view(cls):
        cls.permission_classes = (permissions.IsAuthenticated, IsOwner,)
        return cls.as_view({
            'get': 'retrieve',
            'put': 'update'
        })

    @classmethod
    def user_orders_view(cls):
        cls.permission_classes = (permissions.IsAuthenticated, IsOwner,)
        return cls.as_view({
            'get': 'orders'
        })


class ProductsViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process the requests for products.

    Provides the following view routes and methods:
        products_view (get - list)
        product_create_view (post - create)
        product_view (get - retrieve, put - update)
        product_high_order_view (get - retrieve)

    Implements the following endpoints:
        high_orders: return a list of products that are part of orders with
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
        try:
            high_orders = Order.objects.annotate(
                total=Sum(
                    F('items__quantity') * F('items__product__price'), output_field=DecimalField()
                )
            ).filter(total__gt=100)
        except TypeError:
            return Response({})

        # From the orders, select only those with more than 1 products
        multi_products = [order for order in high_orders if order.items.count() > 1]

        products = self.queryset.filter(orderitem__order__in=multi_products)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def product_search(self, request, payload):
        search_result = self.queryset.filter(Q(name__icontains=payload) | Q(description__icontains=payload))
        serializer = self.serializer_class(search_result, many=True)
        return Response(serializer.data)

    @classmethod
    def products_view(cls):
        return cls.as_view({
            'get': 'list'
        })

    @classmethod
    def product_create_view(cls):
        # Just create products if authenticated and staff
        cls.permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
        return cls.as_view({
            'post': 'create'
        })

    @classmethod
    def product_view(cls):
        # Due to the same name, permissions won't be applied, but TODO: should be applied to `PUT`
        return cls.as_view({
            'get': 'retrieve',
            'put': 'update'
        })

    @classmethod
    def product_high_orders_view(cls):
        # Only apply the is_authenticated permission
        return cls.as_view({
            'get': 'high_orders'
        })

    @classmethod
    def product_search_view(cls):
        cls.permission_classes = (permissions.AllowAny,)
        return cls.as_view({
            'get': 'product_search'
        })


class OrdersViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process request to Orders

    Provides the following view routes and methods:
        orders_view (get - list)
        orders_create_view (post - create)
        order_view (get - retrieve, put - update)
    """
    # The model object to perform the queries
    queryset = Order.objects.all()
    # The serializer to process the data objects
    serializer_class = OrderSerializer

    @classmethod
    def orders_view(cls):
        cls.permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)
        return cls.as_view({
            'get': 'list'
        })

    @classmethod
    def orders_create_view(cls):
        cls.permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser,)
        return cls.as_view({
            'post': 'create'
        })

    @classmethod
    def order_view(cls):
        cls.permission_classes = (((permissions.IsAuthenticated & IsOwner) |
                                   (permissions.IsAuthenticated & permissions.IsAdminUser)),)
        return cls.as_view({
            'get': 'retrieve',
            'put': 'update'
        })


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    Class responsible to process Order Items
    Provides the following view routes and methods:
        order_items_view (get - list, post - create)
        order_item_view (get - retrieve, put - update)
    """
    # the model object to perform the queries
    queryset = OrderItem.objects.all()
    # The serializer to process the data objects
    serializer_class = OrderItemSerializer
    # Only allow if authenticated and is owner or if authenticated and is admin

    @classmethod
    def order_items_view(cls):
        return cls.as_view({
            'get': 'list',
            'post': 'create'
        })

    @classmethod
    def order_item_view(cls):
        return cls.as_view({
            'get': 'retrieve',
            'put': 'update'
        })
