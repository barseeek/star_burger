import json

import phonenumbers
from django.db import IntegrityError
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    try:
        order_info = request.data
    except ValueError:
        return Response({
            'error': "Bad request"
        }, status=status.HTTP_400_BAD_REQUEST)

        # Валидация списка продуктов
    if not order_info.get('products') or not isinstance(order_info.get('products'), list):
        return Response({
            'error': "No products in order"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        phone_number = phonenumbers.parse(order_info.get('phonenumber'), 'RU')
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError
        if (Order.objects.filter(
            phone=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        ).exists()):
            raise IntegrityError
    except (phonenumbers.NumberParseException, ValueError):
        return Response({
            'error': "Invalid phone number"
        }, status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response({
            'error': "This phone number is using, try another one"
        }, status=status.HTTP_400_BAD_REQUEST)
    if not order_info.get('firstname') or not isinstance(order_info.get('firstname'), str):
        return Response({
            'error': "Invalid firstname"
        }, status=status.HTTP_400_BAD_REQUEST)
    if not order_info.get('lastname') or not isinstance(order_info.get('lastname'), str):
        return Response({
            'error': "Invalid lastname"
        }, status=status.HTTP_400_BAD_REQUEST)
    if not order_info.get('address') or not isinstance(order_info.get('address'), str):
        return Response({
            'error': "Invalid address"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(
        first_name=order_info.get('firstname'),
        last_name=order_info.get('lastname'),
        phone=phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164),
        address=order_info.get('address')
    )

    for product_info in order_info['products']:
        try:
            product = Product.objects.get(id=product_info['product'])
        except Product.DoesNotExist:
            order.delete()
            return Response({
                'error': f"Product with id {product_info['product']} does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=product_info['quantity']
        )

    return Response({
        'success': f'Created order {order.pk}'
    }, status=status.HTTP_201_CREATED)
