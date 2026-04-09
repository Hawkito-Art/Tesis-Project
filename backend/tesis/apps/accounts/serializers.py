from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import BlockedIP, LoginAttempt, Role, UserRole

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este email.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'email_verified', 'is_active', 'is_staff',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields


class UserMeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'email_verified', 'created_at',
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'user_email', 'role_name', 'created_at']
        read_only_fields = ['created_at']


class LoginAttemptSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoginAttempt
        fields = ['id', 'email', 'ip_address', 'success', 'attempted_at']
        read_only_fields = fields


class BlockedIPSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlockedIP
        fields = ['id', 'ip_address', 'reason', 'blocked_at', 'is_active']
        read_only_fields = ['blocked_at']
