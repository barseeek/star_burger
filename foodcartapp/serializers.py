import phonenumbers
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Product, OrderItem, Order


class OrderItemSerializer(ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')

    def create(self, validated_data):
        return OrderItem.objects.create(**validated_data)


class OrderSerializer(ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    phonenumber = PhoneNumberField(source='phone')
    address = serializers.CharField()

    class Meta:
        model = Order
        fields = ('id', 'firstname', 'lastname', 'phonenumber', 'address', 'products')

    @transaction.atomic
    def create(self, validated_data):
        products_data = self.initial_data['products']
        validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for item_data in products_data:
            order_item = OrderItemSerializer(data=item_data)
            order_item.is_valid(raise_exception=True)
            order_item.save(order=order, price=Product.objects.get(pk=item_data['product']).price)
        return order
