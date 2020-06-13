from rest_framework import serializers
from django.contrib.auth import password_validation

from .models import User, Product, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        extra_kwargs = {
            'password': {'write_only': True},
        }
        model = User
        fields = (
            'id',
            'email',
            'password',
            'password_confirmation',
            'birth_date',
        )

    def validate(self, clean_data):
        password = clean_data.get('password')
        password_confirmation = clean_data.pop('password_confirmation')

        if password_validation.validate_password(password) is None and password == password_confirmation:
            return clean_data
        raise serializers.ValidationError({'password_confirmation': "Passwords do not match"})


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price'
        )

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price must be a positive value')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'order',
            'product',
            'quantity',
            'item_total'
        )

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than or equal to 1')
        return value


class OrderSerializer(serializers.ModelSerializer):
    # Let's consider a nested relationship
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'items',
            'order_total',
        )
