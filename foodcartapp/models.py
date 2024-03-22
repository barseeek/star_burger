from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQueryset(models.QuerySet):

    def total_price(self):
        if self:
            return Sum(F('items__price') * F('items__quantity'))
        return 0


class Order(models.Model):
    class OrderPaymentType(models.TextChoices):
        CASH = 'cash', _('Наличные')
        CARD = 'card', _('Картой онлайн')

    class OrderStatus(models.TextChoices):
        CREATED = 'created', _('Создан')
        PROCESSED = 'processed', _('Обработан')
        COOKING = 'cooking', _('Готовится')
        DELIVERED = 'delivered', _('Доставлен')

    address = models.CharField(max_length=255, verbose_name='Адрес')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = PhoneNumberField(verbose_name='Мобильный номер')
    payment_type = models.CharField(choices=OrderPaymentType.choices, max_length=10,
                                    verbose_name='Тип оплаты', default=OrderPaymentType.CARD)
    status = models.CharField(choices=OrderStatus.choices, max_length=20,
                              verbose_name='Тип оплаты', default=OrderStatus.CREATED)
    comment = models.TextField(verbose_name='Комментарий', blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания', blank=True)
    processed_at = models.DateTimeField(verbose_name='Дата звонка', validators=[MinValueValidator(created_at)],
                                        blank=True, null=True)
    delivered_at = models.DateTimeField(verbose_name='Дата доставки', validators=[MinValueValidator(created_at)],
                                        blank=True, null=True)
    cook = models.ForeignKey(to=Restaurant, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Где приготовлен', related_name='cook_orders')
    objects = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.address}"

    def update_status(self):
        """Метод для обновления статуса заказа для менеджера"""
        if self.delivered_at:
            self.status = self.OrderStatus.DELIVERED
            self.save()
            return self.status
        elif self.cook:
            self.status = self.OrderStatus.COOKING
            self.save()
            return self
        elif self.processed_at:
            self.status = self.OrderStatus.PROCESSED
            self.save()
            return self.status
        else:
            self.status = self.OrderStatus.CREATED
            self.save()
            return self.status


class OrderItem(models.Model):
    order = models.ForeignKey(to='Order', on_delete=models.CASCADE, verbose_name="Заказ", related_name="items")
    product = models.ForeignKey(to='Product', on_delete=models.SET_DEFAULT, null=True, verbose_name="Товар",
                                default=None)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Стоимость',
                                validators=[MinValueValidator(0)], null=True)

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"Заказ №{self.order.id}, {self.product.name} - {self.quantity} шт."
