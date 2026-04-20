from django.urls import path

from .views import BudgetItemViewSet, BudgetViewSet

app_name = 'budget'

budget_list = BudgetViewSet.as_view({'get': 'list', 'post': 'create'})
budget_detail = BudgetViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)
budget_item_list = BudgetItemViewSet.as_view({'get': 'list', 'post': 'create'})
budget_item_detail = BudgetItemViewSet.as_view(
    {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
)

urlpatterns = [
    path('budgets/', budget_list, name='budget-list'),
    path('budgets/<int:pk>/', budget_detail, name='budget-detail'),
    path('budget-items/', budget_item_list, name='budget-item-list'),
    path('budget-items/<int:pk>/', budget_item_detail, name='budget-item-detail'),
]
