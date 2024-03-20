import phonenumbers
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import Product, OrderItem, Order


class OrderItemSerializer(ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderSerializer(ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    firstname = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')
    phonenumber = serializers.CharField(source='phone')
    address = serializers.CharField()

    class Meta:
        model = Order
        fields = ('id', 'firstname', 'lastname', 'phonenumber', 'address', 'products')

    def validate_phonenumber(self, value):
        try:
            phone_number = phonenumbers.parse(value, 'RU')
            if not phonenumbers.is_valid_number(phone_number):
                raise serializers.ValidationError("Invalid phone number")
            return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number")

