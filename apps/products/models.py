from django.db import models

from apps.products.constant import (
    ADJUSTMENT_TYPE,
    PRODUCT_TYPE_CHOICES,
    PRODUCT_TAX,
    TAX_METHOD,
    BARCODE_PAPER_SIZE,
    SALE_STATUS,
    ORDER_TAX,    
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
        return self.product_name


class Barcode(CommonInfo):
    information = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="barcode_info"
    )
    barcode_image = models.ImageField(upload_to="media/barcode-image/", blank=True, null=True)
    papersize = models.CharField(choices=BARCODE_PAPER_SIZE, max_length=20)


class Adjustment(CommonInfo):
    warehouse = models.OneToOneField(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    type = models.CharField(choices=ADJUSTMENT_TYPE,max_length=15,default=ADJUSTMENT_TYPE[0][0])

    def __str__(self) -> str:
        return self.warehouse
    


class Purchase(CommonInfo):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_warehouse",
    )
    supplier = models.ForeignKey(
        "accounts.Supplier",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_supplier",
    )
    product = models.ManyToManyField(Product)
    order_tax = models.CharField(choices=ORDER_TAX, max_length=10)
    order_discount = models.FloatField()
    shipping = models.FloatField()
    sales_status = models.CharField(choices=SALE_STATUS, max_length=15)
    purchase_note = models.TextField()

    def __str__(self) -> str:
        return self.supplier.supplier_code


class Sales(CommonInfo):
    customer = models.ForeignKey(
        "accounts.Customer",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_customer",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_warehouse",
    )
    biller = models.ForeignKey(
        "accounts.Biller", on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_biller"
    )
    product = models.ManyToManyField(Product)
    sales_tax = models.CharField(choices=ORDER_TAX, max_length=10)
    discount = models.FloatField()
    shipping = models.FloatField()
    sales_status = models.CharField(choices=SALE_STATUS, max_length=15)
    payment_status = models.CharField(choices=SALE_STATUS, max_length=15)
    sales_image = models.ImageField(upload_to="sales/", blank=True, null=True)
    sales_note = models.TextField()
    staff_remark = models.TextField()


class Invoice(CommonInfo):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_warehouse",
    )
    supplier = models.ForeignKey(
        "accounts.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_supplier",
    )

    class Meta:
        abstract=True 

class PurchaseInvoice(Invoice):
    purchases = models.OneToOneField(Purchase,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self) -> str:
        return self.purchases.product

class SalesInvoice(Invoice):
    sales = models.OneToOneField(Sales,on_delete=models.SET_NULL,null=True,blank=True)