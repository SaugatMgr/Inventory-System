from django.db import models

from apps.products.constant import (
    PRODUCT_TYPE_CHOICES,
    PRODUCT_TAX,
    TAX_METHOD,
    BARCODE_PAPER_SIZE,
)

from utils.threads import get_request
from utils.models import (
    CommonInfo,
    Address,
)
from utils.validation_for_phone_number import (
    validate_mobile_number
)


class Brand(CommonInfo):
    brand_name = models.CharField(max_length=30)
    brand_image = models.ImageField(
        upload_to="profile/", blank=True, null=True)

    def __str__(self):
        return self.brand_name


class Category(CommonInfo):

    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(CommonInfo):

    name = models.CharField(max_length=64)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return self.name


class Unit(CommonInfo):
    unit_name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=5)

    def __str__(self):
        return self.short_name


class Warehouse(CommonInfo, Address):
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(
        max_length=15, null=False, unique=True, validators=[validate_mobile_number]
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Product(CommonInfo):
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(
        choices=PRODUCT_TYPE_CHOICES, max_length=30)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="product_category"
    )
    product_code = models.IntegerField()
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="brand"
    )
    barcode = models.CharField(max_length=100)
    product_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="product_unit"
    )
    product_price = models.FloatField()
    expense = models.FloatField()
    unit_price = models.FloatField()
    product_tax = models.CharField(choices=PRODUCT_TAX, max_length=10)
    tax_method = models.CharField(choices=TAX_METHOD, max_length=20)
    discount = models.FloatField()
    stock_alert = models.IntegerField()
    product_image = models.ImageField(
        upload_to="profile/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    price_difference_in_warehouse = models.BooleanField(default=True)
    warehouse = models.ManyToManyField(Warehouse)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="product_user"
    )
    has_expiry_date = models.BooleanField(default=True)
    add_promotional_sale = models.BooleanField(default=True)
    has_multi_variant = models.BooleanField(default=True)
    has_imie_code = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        current_user = get_request().user
        self.user = current_user
        self.created_by = current_user
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.created_by.full_name


class Barcode(CommonInfo):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="barcode_info"
    )
    papersize = models.CharField(choices=BARCODE_PAPER_SIZE, max_length=20)
