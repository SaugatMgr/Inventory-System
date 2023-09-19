from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    UnitViewSet,
)

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("brands", BrandViewSet)
router.register("categories", CategoryViewSet)
router.register("sub-categories", SubCategoryViewSet)
router.register("units", UnitViewSet)
