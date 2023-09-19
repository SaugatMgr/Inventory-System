from rest_framework import serializers
from apps.products.models import (
    Warehouse,
    Brand,
    Category,
    SubCategory,
    Product,
    Unit,
    Barcode,

)
from apps.accounts.serializers import UserSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            'id',
            'name',
            'phone',
            'email',
        )


class BrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id",
            "brand_name",
            "brand_image",
        )


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = (
            "id",
            "name",
            "category",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
        )


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "unit_name", "short_name")


class ProductSerializer(serializers.ModelSerializer):
    # warehouse = WarehouseSerializer(many=True)
    class Meta:
        model = Product
        fields = (
            "id",
            "product_name",
            "product_type",
            "product_code",
            "product_unit",
            "unit_price",
            "product_price",
            "product_tax",
            "tax_method",
            "discount",
            "stock_alert",
            "expense",
            "category",
            "brand",
            "warehouse",
            "barcode",
            "product_image",
            "featured",
            "price_difference_in_warehouse",
            "add_promotional_sale",
            "has_expiry_date",
            "has_multi_variant",
            "has_imie_code",
        )

    def create(self, validated_data):
        warehouse_data = validated_data.pop(
            'warehouse', [])  # Extract warehouse data

        # Create the product instance with other fields
        product = Product.objects.create(**validated_data)

        for warehouse_info in warehouse_data:
            warehouse_id = warehouse_info.id

            try:
                warehouse_obj = Warehouse.objects.get(id=warehouse_id)
                product.warehouse.add(warehouse_obj)
            except Warehouse.DoesNotExist:
                pass

        return product


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = (
            "information",
            "papersize",
        )


class GETProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializers()
    category = CategorySerializer()
    product_unit = UnitSerializer()
    user = UserSerializer()
    modified_by = UserSerializer()
    warehouse = WarehouseSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"


class GetCategorySeralizer(serializers.ModelSerializer):
    user = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Category
        fields = (
            "user",
            "modified_by",
            "main_category",
            "sub_category",
        )


class GetUnitSeralizer(serializers.ModelSerializer):
    created_by = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Unit
        fields = (
            "created_by",
            "modified_by",
            "unit_name",
            "short_name",
        )


class GetBrandSeralizer(serializers.ModelSerializer):
    created_by = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Brand
        fields = (
            "created_by",
            "modified_by",
            "brand_name",
            "brand_image",
        )
