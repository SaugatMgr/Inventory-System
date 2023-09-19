from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
import pyotp

from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
)


from apps.accounts.models import (
    User,
    Customer,
    Supplier,
    Biller,
    Warehouse,
)
from apps.accounts.serializers import (
    UserSerializer,
    GetUserListSerializer,
    SupplierSerializer,
    GetSupplierSerializer,
    CustomerSerializer,
    GetCustomerSerializer,
    BillerSerializer,
    GetBillerSerializer,
    WarehouseSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    ForgotPasswordSerializer,
)
from apps.accounts.pagination import MyPagination
from utils.permissions import (
    IsSupplierPermission,
)
from utils.send_otp_to_email import send_otp_email


class CommonModelViewset(ModelViewSet):
    pagination_class = MyPagination


class UserViewSet(CommonModelViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["full_name", ]

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
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
        # if self.request.user.is_superuser and self.action == "list":
        #     return GetUserListSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        return super().get_serializer_class()

    @action(permission_classes=[IsAuthenticated],
            methods=['post'], url_path='change-password', detail=True)
    def change_password(self, request, pk=None):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data["password"]
        old_password = serializer.validated_data["old_password"]

        if not request.user.check_password(old_password):
            return Response({"message": "Old password is not correct"})

        if password is not None:
            user.set_password(password)
            user.save()

        return Response({"success": ["Password reset successfully"]}, status=status.HTTP_200_OK)

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class CustomerViewSet(CommonModelViewset):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
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
            return GetCustomerSerializer
        return super().get_serializer_class()


class SupplierViewSet(CommonModelViewset):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser | IsSupplierPermission],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
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
            return GetSupplierSerializer
        return super().get_serializer_class()

    def create(self, request):
        request.data["supplier_code"] = f"SC-{Supplier.objects.count()}"
        serializers = SupplierSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class BillerViewSet(CommonModelViewset):
    queryset = Biller.objects.all()
    serializer_class = BillerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,]
    filterset_fields = ["user", ]
    search_fields = ['user__full_name']

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
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
            return GetBillerSerializer
        return super().get_serializer_class()

    def create(self, request):
        request.data["biller_code"] = f"BC-{Biller.objects.count()}"
        serializers = BillerSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class WarehouseViewSet(CommonModelViewset):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name']
    ordering_fields = ['name', 'email']

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]


def generate_otp():
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key)

    return otp.now()


class ForgotPasswordViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "reset_password":
            return ForgotPasswordSerializer
        return super().get_serializer_class()

    def create(self, request):

        # using email serializer to validate the user password
        email_serializer = PasswordResetRequestSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        email = email_serializer.validated_data['email']

        # getting the user after validating email
        user = get_object_or_404(User, email=email)
        otp = generate_otp()
        user.otp = otp
        user.save()

        reset_password_url = f"http://127.0.0.1:8000/api/forgot-password/{user.id}/reset-password/"

        send_otp_email(user.email, reset_password_url, otp)

        return Response({"success": "Email has been sent successfully", "data": {"email": user.id}}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='reset-password', permission_classes=[AllowAny])
    def reset_password(self, request, pk=None):

        user = get_object_or_404(User, id=pk)

        forgot_password_serializer = ForgotPasswordSerializer(
            data=request.data, context={'user': user})
        forgot_password_serializer.is_valid(raise_exception=True)
        password = forgot_password_serializer.validated_data['password']

        user.set_password(password)
        user.save()

        # return success response after updating the password
        return Response({"success": "Password reset successful"}, status=status.HTTP_202_ACCEPTED)


class RegisterUserViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = RegisterSerializer
