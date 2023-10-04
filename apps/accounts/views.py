from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from django.shortcuts import get_object_or_404

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
    # Warehouse,
    OTP,
)
from apps.accounts.serializers import (
    UserSerializer,
    SupplierSerializer,
    GetSupplierSerializer,
    CustomerSerializer,
    GetCustomerSerializer,
    BillerSerializer,
    GetBillerSerializer,
    # WarehouseSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    ForgotPasswordSerializer,
)
from apps.accounts.pagination import MyPagination
from utils.send_otp_to_email import send_otp_email
from django.conf import settings


class CommonModelViewset(ModelViewSet):
    pagination_class = MyPagination


class UserViewSet(CommonModelViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes_by_action = {
        "list": [IsAuthenticated],
        "create": [IsAdminUser],
        "retrieve": [IsAdminUser],
        "patch": [IsAdminUser],
        "destroy": [IsAdminUser],
        "register": [AllowAny],
        "change_password": [IsAuthenticated],
        "forgot_password": [AllowAny],
        "reset_password": [AllowAny],
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
        if self.action == "register":
            return UserSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        if self.action == "forgot_password":
            return PasswordResetRequestSerializer
        if self.action == "reset_password":
            return ForgotPasswordSerializer
        return super().get_serializer_class()

    @action(methods=["post"], url_path="register", detail=False)
    def register(self, request, pk=None):
        register_serializer = UserSerializer(data=request.data)
        register_serializer.is_valid(raise_exception=True)
        register_serializer.save()

        return Response(
            {"message": "User Registration Successful."}, status=status.HTTP_201_CREATED
        )

    @action(methods=["post"], url_path="change-password", detail=True)
    def change_password(self, request, pk=None):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        password = serializer.validated_data["password"]

        if not request.user.check_password(old_password):
            return Response({"message": "Old password is not correct."})

        if password is not None:
            user.set_password(password)
            user.save()

        return Response(
            {"message": "Password reset successfully."}, status=status.HTTP_200_OK
        )

    @action(
        methods=["post"],
        detail=False,
        url_path="forgot-password",
    )
    def forgot_password(self, request, pk=None):
        email_serializer = PasswordResetRequestSerializer(data=request.data)

        email_serializer.is_valid(raise_exception=True)
        email = email_serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        otp = OTP.generate_otp(user=user)

        send_otp_email(user.email, otp)

        return Response(
            {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
        )

    @action(
        methods=["post"],
        detail=True,
        url_path="reset-password",
    )
    def reset_password(self, request, pk=None):
        user = self.get_object()

        forgot_password_serializer = ForgotPasswordSerializer(
            data=request.data, context={"request": request}
        )

        forgot_password_serializer.is_valid(raise_exception=True)
        password = forgot_password_serializer.validated_data["password"]

        user.set_password(password)
        user.save()

        return Response(
            {"message": "Password reset successfully."}, status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        data = request.data
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError({"password": "The two password fields do not match."})

        data.pop("confirm_password", None)
        data["password"] = make_password(password)

        user_serializer = UserSerializer(data=data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        return Response(
            {"message": "User Registration Successful."}, status=status.HTTP_201_CREATED
        )

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
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

    def create(self, request):
        request.data["user"]["role"] = "Customer"

        user_serializer = UserSerializer(data=request.data["user"])
        customer_serializer = self.get_serializer(data=request.data)

        user_serializer.is_valid(raise_exception=True)
        customer_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = user_serializer.save()
            customer_serializer.save(user=user)

        response_data = {
            "message": "Customer created successfully",
            "data": customer_serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class SupplierViewSet(CommonModelViewset):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

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
            return GetSupplierSerializer
        return super().get_serializer_class()

    def create(self, request):
        request.data["user"]["role"] = "Supplier"

        user_serializer = UserSerializer(data=request.data["user"])
        supplier_serializer = self.get_serializer(data=request.data)

        user_serializer.is_valid(raise_exception=True)
        supplier_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = user_serializer.save()
            supplier_serializer.save(
                user=user,
                supplier_code=f"{settings.SUPPLIER_CODE}{Supplier.objects.count()}",
            )

        response_data = {
            "message": "Supplier created successfully",
            "data": supplier_serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class BillerViewSet(CommonModelViewset):
    queryset = Biller.objects.all()
    serializer_class = BillerSerializer

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
        request.data["user"]["role"] = "Biller"

        user_serializer = UserSerializer(data=request.data["user"])
        biller_serializer = self.get_serializer(data=request.data)

        user_serializer.is_valid(raise_exception=True)
        biller_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = user_serializer.save()
            biller_serializer.save(
                user=user, biller_code=f"{settings.BILLER_CODE}{Biller.objects.count()}"
            )

        response_data = {
            "message": "Biller created successfully",
            "data": biller_serializer.data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
