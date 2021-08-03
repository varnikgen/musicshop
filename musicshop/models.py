from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone



class MediaType(models.Model):
    """Медианоситель"""

    name = models.CharField(max_length=100, verbose_name="Название медианосителя")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Медианоситель'
        verbose_name_plural = 'Медианосители'


class Member(models.Model):
    """Музыкант"""
    
    name = models.CharField(max_length=255, verbose_name="Имя музыканта")
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Музыкант'
        verbose_name_plural = 'Музыканты'

class Genre(models.Model):
    """Музыкальный жанр"""

    name = models.CharField(max_length=50, verbose_name='Название жанра')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Artist(models.Model):
    """Исполнитель"""

    name = models.CharField(max_length=255, verbose_name="Исполнитель/Группа")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, verbose_name="Участник", related_name="artist")
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class Album(models.Model):
    """Альбом исполнителя"""

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="Исполнитель")
    name = models.CharField(max_length=255, verbose_name="Название альбома")
    media_type = models.ForeignKey(MediaType, on_delete=models.CASCADE, verbose_name="Носитель")
    songs_list = models.TextField(verbose_name="Трек лист")
    release_date = models.DateField(verbose_name="Дата релиза")
    slug = models.SlugField()
    description = models.TextField(verbose_name="Описание", default=".описаниепоявится позже")
    stock = models.IntegerField(verbose_name="На складе", default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Цена")
    offer_of_the_week = models.BooleanField(default=False, verbose_name="Предложение недели?")

    def __str__(self):
        return f"{self.id} | {self.artist.name} |  {self.name}"

    @property
    def ct_model(self):
        return self._meta.model_name

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'


class CartProduct(models.Model):
    """Продукт корзины"""

    user = models.ForeignKey('Customer', verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name="Корзина", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")

    def __str__(self):
        return f"Продукт: {self.content_object.name} (для корзины)"

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_type.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'

    
class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey('Customer', verbose_name="Покупатель", on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, null=True, related_name="related_cart", verbose_name="Продукты для корзины",)
    total_products = models.IntegerField(default=0, verbose_name="Общее кол-во товара")
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Общая цена")
    in_order = models.BooleanField(default=False)
    for_anonimus_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    
class Order(models.Model):
    """Заказ пользователя"""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ получен покупателем'),
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка'),
    )

    customer = models.ForeignKey('Customer', verbose_name='Покупатель', related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES)
    comment = models.TextField(verbose_name='Коментарий к заказу', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания заказа', auto_now=True)
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now )

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

class Customer(models.Model):
    """Покупатель"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name='Активный?')
    customer_orders = models.ManyToManyField(Order, blank=True, verbose_name='Заказы покупателя', related_name='related_customer')
    wishlist = models.ManyToManyField(Album, verbose_name='Список ожидаемого', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        return f"{self.user.username}"

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural= 'Покупатели'


class Notification(models.Model):
    """Уведомления"""

    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='Получатель')
    text = models.TextField(verbose_name='Текст уведомления')
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Уведомление для {self.recipient.user.username} | id={self.id}"
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
