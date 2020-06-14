from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import Sum, F, DecimalField
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field
    the username field is replaced with the password.
       This replaces the Django base user manager for the admin panel and the superuser creation process
    """

    use_in_migrations = True

    def _create_user(self,email,password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('the email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must have is_staff as True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_superuser as True')

        return self._create_user(email, password, **extra_fields)


# Create your models here.
class Base(models.Model):
    """Base class to be inherited by all models of the API

    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)  # Used for logical deletion

    class Meta:
        abstract = True


class User(AbstractUser):
    """An extended user class, expanding from the AbstractUser to be used in the
    django admin manager.
    This class replaces the username field with the email field.
    """
    # Modifications needed to set email as the username/authentication/login field
    username = None
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)

    # Use email as username field
    USERNAME_FIELD = 'email'
    # remove the email from the required fields. It is redundant now!
    REQUIRED_FIELDS = []

    # The specific manager for the extended user
    objects = UserManager()


class Product(Base):
    """Class used to represent and persist the products data

    Fields Persisted: 3 + Base
        name - String(255)
        description - String
        price - Decimal > 0.00

    Fields Computed: None
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=False)
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))])

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['id']

    def __str__(self):
        return f'{self.name} - {self.price}'


class Order(Base):
    """Class used to represent and persist the orders data.
        Order is related to a user. Order items are implemented in separate class.
        Fields persisted: 1 + Base
            user: The user related to this order

        Fields Computed: 1
            order_total: Decimal
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['id']

    def __str__(self):
        return f'Order placed at {self.created} by {self.user}'

    @property
    def order_total(self):
        total = self.items.aggregate(
            order_total=Sum(F('quantity') * F('product__price'),
                            output_field=DecimalField())).get('order_total')
        return total


class OrderItem(Base):
    """Class used to represent and to persist the item in an order
    Fields Persisted: 3 + Base
        order<Order>: The order related to this orderItem
        product<Product>: The product related to this orderItem
        quantity<int>: The quantity ordered

    Fields Computed: 1
        item_total<Decimal>: The price total (product.price * quantity)
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('order', 'product')

    @property
    def item_total(self):
        total = self.product.price * self.quantity
        return total
