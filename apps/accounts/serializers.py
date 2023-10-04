import pyotp
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import (
    OTP,
    User,
    Customer,
    Biller,
    Supplier,
    # Warehouse,
)


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone",
            "email",
            "username",
            "gender",
            "country",
            "city",
            "address",
            "zip_code",
            "password",
            "confirm_password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class SupplierSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Supplier
        fields = (
            "id",
            "user",
            "company",
        )


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
            "supplier_name",
            "customer_group",
            "reward_point",
        )


class BillerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Biller
        fields = (
            "id",
            "user",
            "NID",
            "warehouse",
        )


# class WarehouseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Warehouse
#         fields = (
#             "id",
#             "name",
#             "phone",
#             "email",
#         )


class GetSupplierSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Supplier
        fields = (
            "id",
            "user",
            "supplier_code",
            "company",
        )


class GetBillerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # warehouse = WarehouseSerializer()

    class Meta:
        model = Biller
        fields = (
            "id",
            "user",
            "biller_code",
            "NID",
            # "warehouse",
        )


class GetCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = (
            "id",
            "user",
            "supplier_name",
            "customer_group",
            "reward_point",
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ("old_password", "password", "confirm_password")

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old password": "Sorry your old password doesn't match"}
            )
        return value

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({"password": "Your password donot match"})
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ("email")


class ForgotPasswordSerializer(serializers.ModelSerializer):
    otp = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["otp", "password", "confirm_password"]

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({"message": "The two password fields do not match"})
        return data

    def validate_otp(self, value):
        
        user = self.context["request"].user

        try:
            otp_obj = OTP.objects.get(user=user)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("OTP not found.")

        secret_key = otp_obj.secret_key

        otp_instance = pyotp.TOTP(secret_key)
        
        if otp_instance.verify(value, valid_window=3):
            otp_obj.delete()
        else:
            otp_obj.delete()
            raise serializers.ValidationError("Invalid OTP.")
