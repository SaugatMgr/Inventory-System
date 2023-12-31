import os
import uuid
import barcode
from barcode.writer import ImageWriter
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status

from apps.products.models import (
    Brand,
    Category,
    SubCategory,
    Product,
    Unit,
    Warehouse,
    Barcode,
    Purchase,
    Sales,
    PurchaseInvoice,
    # SalesInvoice,
    Adjustment,
)
from apps.products.serializers import (
    AdjustmentSerializer,
    BarcodeSerializer,
    BrandSerializers,
    CategorySerializer,
    GetAdjustmentSeralizer,
    GetBarcodeSerializer,
    GetPurachseSerializer,
    ProductSerializer,
    GETProductSerializer,
    PurchaseInvoiceSerializer,
    PurchaseSerializer,
    SalesSerializer,
    UnitSerializer,
    GetCategorySeralizer,
    GetUnitSeralizer,
    GetBrandSeralizer,
    WarehouseSerializer,
    SubCategorySerializer,
)
from apps.accounts.pagination import MyPagination

from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)


class CommonModelViewSet(ModelViewSet):
    pagination_class = MyPagination


class BrandViewSet(CommonModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializers
    http_method_names = ["get", "post", "put", "delete"]
    filterset_fields = ["brand_name"]

    def create(self, request, *args, **kwargs):
        serializers = BrandSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user, modified_by=None)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializers = BrandSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(modified_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetBrandSeralizer
        return super().get_serializer_class()


class SubCategoryViewSet(CommonModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


class CategoryViewSet(CommonModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        serializers = CategorySerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user, modified_by=None)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetCategorySeralizer
        return super().get_serializer_class()


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["=short_name"]
    ordering_fields = ["short_name"]

    def create(self, request, *args, **kwargs):
        serializers = UnitSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetUnitSeralizer
        return super().get_serializer_class()


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    filterset_fields = ["created_by"]
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAuthenticated],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GETProductSerializer
        return super().get_serializer_class()


class WarehouseViewset(ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    http_method_names = ['get', 'post', 'put', 'delete']


class BarcodeViewSet(ModelViewSet):
    queryset = Barcode.objects.all()
    serializer_class = BarcodeSerializer

    def create(self, request, *args, **kwargs):
        product_infromation = request.data.get("information")
        get_current_product = Product.objects.get(id=product_infromation)
        get_current_product_code = get_current_product.product_code
        if not get_current_product_code:
            # print(product_infromation.product_code)
            return Response(
                {"error": "Product code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        barcode_class = barcode.get_barcode_class("code128")
        code = barcode_class(get_current_product_code, writer=ImageWriter())

        unique_filename = f"barcode_{uuid.uuid4()}"

        directory_path = "media/barcode-image/"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        barcode_image = code.save(f"barcode-image/{unique_filename}")

        serializer = BarcodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(barcode_image=barcode_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetBarcodeSerializer
        return super().get_serializer_class()


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetPurachseSerializer
        return super().get_serializer_class()


class SalesViewSet(ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer


class PurchaseInvoiceViewSet(ModelViewSet):
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer

class AdjustmentViewset(ModelViewSet):
    queryset = Adjustment.objects.all()
    serializer_class = AdjustmentSerializer

    def create(self, request):
        serializer = AdjustmentSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('quantity')
        adjustment = Adjustment.objects.create(**serializer.validated_data)
        serializer = AdjustmentSerializer(adjustment)
        return Response({"data" : serializer.data}) 
    
    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetAdjustmentSeralizer
        return super().get_serializer_class()
