from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip()
        password = attrs.get("password")
        request = self.context.get("request")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        normalized_email = User.objects.normalize_email(email)
        user = authenticate(request=request, username=normalized_email, password=password)
        if not user:
            user = authenticate(request=request, email=normalized_email, password=password)
        if not user:
            candidate = User.objects.filter(email__iexact=normalized_email).first()
            if candidate and candidate.check_password(password) and candidate.is_active:
                user = candidate

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User is inactive")
        attrs["user"] = user
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "is_active", "date_joined")
