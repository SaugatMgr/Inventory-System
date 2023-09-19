from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    UnitViewSet,
    BarcodeViewSet,
    PurchaseViewSet,
    SalesViewSet,
    PurchaseInvoiceViewSet,
    AdjustmentViewset,
)

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("brands", BrandViewSet)
router.register("categories", CategoryViewSet)
router.register("sub-categories", SubCategoryViewSet)
router.register("units", UnitViewSet)
router.register("barcode", BarcodeViewSet)
router.register("purchase", PurchaseViewSet)
router.register("sales", SalesViewSet)
router.register("purchase-invoice", PurchaseInvoiceViewSet)
router.register("adjustment", AdjustmentViewset)
