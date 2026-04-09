from django.urls import path

from .views import LoginAPIView, LogoutAPIView, MeAPIView, RefreshAPIView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='auth-login'),
    path('refresh/', RefreshAPIView.as_view(), name='auth-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='auth-logout'),
    path('me/', MeAPIView.as_view(), name='auth-me'),
]
