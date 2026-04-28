from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import Role
from .permissions import AccountsDirectoryPermission
from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserMeSerializer,
    UserUpdateSerializer,
)
from .services import authenticate_user, revoke_refresh_token

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = authenticate_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

        return Response(
            {'access': tokens.access, 'refresh': tokens.refresh},
            status=status.HTTP_200_OK,
        )


class RefreshAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        revoke_refresh_token(refresh_token=serializer.validated_data['refresh'])
        return Response({'detail': 'Logout exitoso.'}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    permission_classes = [IsAuthenticated, AccountsDirectoryPermission]
    filterset_fields = ['email_verified', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['id', 'email', 'created_at', 'updated_at']
    ordering = ['-id']

    def perform_destroy(self, instance):
        instance.delete()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('partial_update', 'update'):
            return UserUpdateSerializer
        return UserDetailSerializer


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all().order_by('-id')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, AccountsDirectoryPermission]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'created_at']
    ordering = ['-id']
