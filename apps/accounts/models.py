import uuid
import pyotp
from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.accounts.managers import CustomUserManager
from apps.accounts.constant import (
    GENDER_CHOICES,
    ROLE_CHOICES,
    CUSTOMER_GROUP_CHOICES,
)
# from apps.products.models import Warehouse
from utils.validation_for_phone_number import (
    validate_mobile_number,
    valid_emails,
)
from utils.models import (
    CommonInfo,
    Address,
)


class User(AbstractUser, Address):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15, null=False, unique=True, validators=[validate_mobile_number]
    )
    email = models.EmailField(unique=True, validators=[valid_emails])
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    profile_image = models.ImageField(upload_to="profile/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "full_name",
        "username",
        "phone",
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Supplier(CommonInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    supplier_code = models.CharField(max_length=50)

    def __str__(self):
        return self.user.full_name


class Customer(CommonInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=150)
    customer_group = models.CharField(max_length=10, choices=CUSTOMER_GROUP_CHOICES)
    reward_point = models.IntegerField(default=0)

    def __str__(self):
        return self.user.full_name


class Biller(CommonInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    NID = models.CharField(max_length=13)
    # warehouse = models.ForeignKey(
    #     Warehouse,
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )
    biller_code = models.CharField(max_length=50)

    def __str__(self):
        return self.user.full_name


class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32)
    otp_code = models.CharField(max_length=6)

    @classmethod
    def generate_otp(cls, user):
        otp_instance, created = cls.objects.get_or_create(user=user)

        secret_key = pyotp.random_base32()
        otp = pyotp.TOTP(secret_key)
        otp_code = otp.now()

        otp_instance.secret_key = secret_key
        otp_instance.otp_code = otp_code
        otp_instance.save()

        return otp_code
