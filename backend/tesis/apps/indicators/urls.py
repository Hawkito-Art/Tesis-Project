from django.urls import path

from .views import (
    IndicatorViewSet,
    IndicatorGroupViewSet,
    IndicatorRecordListAPIView,
    IndicatorVariableViewSet,
)

app_name = 'indicators'

indicator_group_list = IndicatorGroupViewSet.as_view({'get': 'list', 'post': 'create'})
indicator_group_detail = IndicatorGroupViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
indicator_list = IndicatorViewSet.as_view({'get': 'list', 'post': 'create'})
indicator_detail = IndicatorViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
indicator_variable_list = IndicatorVariableViewSet.as_view({'get': 'list', 'post': 'create'})
indicator_variable_detail = IndicatorVariableViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
indicator_record_list = IndicatorRecordListAPIView.as_view({'get': 'list'})

urlpatterns = [
    path('groups/', indicator_group_list, name='indicator-groups-list'),
    path('groups/<int:pk>/', indicator_group_detail, name='indicator-groups-detail'),
    path('', indicator_list, name='indicators-list'),
    path('<int:pk>/', indicator_detail, name='indicators-detail'),
    path('variables/', indicator_variable_list, name='indicator-variables-list'),
    path(
        'variables/<int:pk>/',
        indicator_variable_detail,
        name='indicator-variables-detail',
    ),
    path('records/', indicator_record_list, name='indicator-records-list'),
]
