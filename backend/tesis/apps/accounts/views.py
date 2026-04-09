from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .serializers import LoginSerializer, LogoutSerializer, UserMeSerializer
from .services import authenticate_user, revoke_refresh_token


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
