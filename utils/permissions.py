from rest_framework.permissions import (
    BasePermission,
)


class IsSupplierPermission(BasePermission):
    edit_methods = ("POST", "PUT", "PATCH", "DELETE")

    def has_permission(self, request, view):
        if request.user.role == "Supplier" or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj.user and request.method in self.edit_methods
