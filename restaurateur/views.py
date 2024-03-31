from django import forms
from django.db.models import F, Prefetch
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy.distance import distance

from foodcartapp.coordinates import fetch_coordinates, get_place_coordinates_by_address
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderItem
from places.models import Place
from star_burger import settings
from requests.exceptions import ConnectionError, HTTPError

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    items = []
    orders = (Order.objects.
              exclude(status__exact=Order.OrderStatus.DELIVERED).
              annotate(price=Order.objects.total_price()).
              order_by('status'))
    places = {
        place.address: (place.lat, place.lon) if place.lat and place.lon else None
        for place in Place.objects.all()
    }
    for order in orders:
        order_items = OrderItem.objects.filter(order_id=order.id).prefetch_related(
            Prefetch(
                'product__menu_items',
                queryset=RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant'),
                to_attr='available_restaurants'
            )
        )
        restaurant_sets = [set(item.product.menu_items.values_list('restaurant__name', 'restaurant__address')) for item in
                           order_items]
        common_restaurants = set.intersection(*restaurant_sets) if restaurant_sets else set()
        order_coordinates = places.get(order.address)
        # if order_coordinates in places:
        #     order_coordinates = places[order.address]
        # else:
        #     pass#get_place_coordinates_by_address(settings.YANDEX_API_KEY, order.address)
        order.restaurants = []
        for restaurant in list(common_restaurants):
            rest_name, rest_address = restaurant[0], restaurant[1]
            restaurant_coordinates = places.get(rest_address)
            # if restaurant_coordinates in places:
            #     restaurant_coordinates = places[rest_address]
            # else:
            #     pass#get_place_coordinates_by_address(settings.YANDEX_API_KEY, rest_address)

            distance_km = None

            if restaurant_coordinates and order_coordinates:
                distance_km = distance(order_coordinates, restaurant_coordinates).km
            serialized_rest = {
                'name': rest_name,
                'distance_km': distance_km,
                'msg': "{:.2f} км".format(distance_km) if distance_km else 'Ошибка определения координат'
            }
            order.restaurants.append(serialized_rest)
        order.restaurants.sort(key=lambda rest: rest['distance_km'])
        items.append(order)

    return render(request, template_name='order_items.html', context={
        'items': items
    })
