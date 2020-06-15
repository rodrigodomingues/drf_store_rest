from rest_framework.permissions import BasePermission
from .models import Order, OrderItem, User

class IsOwner(BasePermission):
    """
    Custom permission class to allow only the proper user to view/update their data and orders/orders items
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj == request.user
        if isinstance(obj, Order):
            user = User.objects.filter(email=obj.user).first()
            return user == request.user
        if isinstance(obj, OrderItem):
            order = Order.objects.filter(id=obj.order).first()
            return self.has_object_permission(request, view, order)
