from django.db import models
from django.utils.timezone import localtime, localdate


def get_current_time():
    return localtime().time().strftime('%H:%M:%S')


class Table(models.Model):
    name = models.PositiveIntegerField(unique=True)
    is_available = models.BooleanField('Status', default=True, help_text='If the table is free-True, busy-False')

    class Meta:
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'
        ordering = ['is_available']

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    APPETIZERS = 'AP'
    SOUPS = 'SO'
    SALADS = 'SA'
    MAIN_DISHES = 'MD'
    SIDES = 'SI'
    SNACKS = 'SN'
    DESSERTS = 'DE'
    DRINKS = 'DN'
    CATEGORY_CHOISES = [
        (APPETIZERS, 'закуски'),
        (SOUPS, 'супы'),
        (SALADS, 'салаты'),
        (MAIN_DISHES, 'основные блюда'),
        (SIDES, 'гарниры'),
        (SNACKS, 'закуски'),
        (DESSERTS, 'десерты'),
        (DRINKS, 'напитки'),
    ]

    name = models.CharField('Название блюда', max_length=100)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', max_length=1000)
    category = models.CharField('Категории', max_length=2, choices=CATEGORY_CHOISES)

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    table = models.ForeignKey(Table,
                              on_delete=models.CASCADE,
                              verbose_name='Стол')
    start_date = models.DateField(default=localdate, blank=True)
    start_time = models.TimeField(default=get_current_time, blank=True)
    is_active = models.BooleanField(default=True)
    order_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def __str__(self):
        return f'Order №{self.pk}'


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product', verbose_name='Позиция меню')
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_item')
    start_date = models.DateField(default=localdate, blank=True)
    start_time = models.TimeField(default=get_current_time, blank=True)
    count = models.PositiveIntegerField('Product amount', default=1)
    order_item_cost = models.DecimalField('Position cost', max_digits=7, decimal_places=2, default=0)
    is_ready = models.BooleanField(default=False, blank=True)

    def save(self, *args, **kwargs):
        product_cost = Product.objects.get(pk=self.product.id).price
        self.order_item_cost = product_cost * self.count
        order = Order.objects.get(pk=self.order.id)
        order.order_cost += self.order_item_cost
        order.save()
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.count}'




