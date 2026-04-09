from django.urls import path

from .views import EntityViewSet, PeriodViewSet

app_name = 'catalog'

entity_list = EntityViewSet.as_view({'get': 'list', 'post': 'create'})
entity_detail = EntityViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
period_list = PeriodViewSet.as_view({'get': 'list', 'post': 'create'})
period_detail = PeriodViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})

urlpatterns = [
    path('entities/', entity_list, name='entity-list'),
    path('entities/<int:pk>/', entity_detail, name='entity-detail'),
    path('periods/', period_list, name='period-list'),
    path('periods/<int:pk>/', period_detail, name='period-detail'),
]
