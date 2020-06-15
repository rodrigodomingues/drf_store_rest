from rest_framework import serializers
from django.contrib.auth import password_validation

from .models import User, Product, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    """Class responsible to serialize the user data
    validates password
    """
    # field for password confirmation. Does not take part of the model and is only retrieved via request.
    # It is not sent to the response
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        extra_kwargs = {
            # Does not inform the password to the response. Only retrieves via request
            'password': {'write_only': True},
        }
        # To which model is this serializer related to
        model = User
        # Which fields are related to this serialization
        # Field names identical to the model are bounded to the ORM
        fields = (
            'id',
            'email',
            'password',
            'password_confirmation',
            'birth_date',
        )

    def validate(self, clean_data):
        """
        Validates the password and confirms with password_confirmation
        Raises a ValidationError if the validation fails

        :param clean_data: The data as retrieved in the request
        :return: The data as retrieved in the request
        """
        password = clean_data.get('password')
        password_confirmation = clean_data.pop('password_confirmation')
        if password_validation.validate_password(password) is None and password == password_confirmation:
            return clean_data
        raise serializers.ValidationError({'password_confirmation': "Passwords do not match"})


class ProductSerializer(serializers.ModelSerializer):
    """
    Class responsible to serialize the product data
    """
    class Meta:
        # The model related to this serializer
        model = Product
        # Which fields are related to this serialization
        # Field names identical to the model are persisted
        fields = (
            'id',
            'name',
            'description',
            'price'
        )


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Class responsible to serialize the order item data
    """
    class Meta:
        # The model related to this serializer
        model = OrderItem
        # Which fields are related to this serialization
        # Field names identical to the persisted fields in the model are persisted
        fields = (
            'order',
            'product',
            'quantity',
            'item_total'
        )


class OrderSerializer(serializers.ModelSerializer):
    """
    Class responsible to serialize the order data
    """
    # Let's consider a nested relationship.
    # The serializer will bring all the items for this order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        # The model related to this serializer
        model = Order
        # Which fields are related to this serialization
        # Field names identical to the persisted fields in the model are persisted
        fields = (
            'id',
            'user',
            'items',
            'order_total',
        )

