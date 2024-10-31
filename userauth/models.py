# userauth/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    TAILOR = 'TAILOR'
    CUSTOMER = 'CUSTOMER'
    ROLE_CHOICES = [
        (TAILOR, 'Tailor'),
        (CUSTOMER, 'Customer'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER,
        help_text="Role of the user, either Tailor or Customer."
    )
    customer_id = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique identifier for customers, 6 characters."
    )
    customers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='tailors',
        blank=True,
        help_text="Customers associated with a tailor."
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Generate a 6-character unique customer_id only for customers if not already set
        if self.role == self.CUSTOMER and not self.customer_id:
            self.customer_id = self.generate_customer_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_customer_id():
        # Generate a random 6-character alphanumeric ID
        while True:
            customer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not CustomUser.objects.filter(customer_id=customer_id).exists():
                return customer_id
