"""
URL configuration for financial_planner project.

"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    BudgetListCreateView,
    GoalListCreateView,
    SpendingSummaryView,
    BulkGoalCreateView, 
    IncomeListCreateView,
    ExpenseListCreateView,
    DebtListCreateView,
    BudgetCategoryListCreateView,
    NotificationListView,
    LoginView,
    RegisterView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/',LoginView.as_view() , name='login'),
    path('register/',RegisterView.as_view() , name='register'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('budget/', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('goals/', GoalListCreateView.as_view(), name='goal-list-create'),
    path('goals/bulk-create/', BulkGoalCreateView.as_view(), name='bulk-goal-create'),
    path('spending-summary/', SpendingSummaryView.as_view(), name='spending-summary'),
    path('income/', IncomeListCreateView.as_view(), name='income-list-create'),
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('debts/', DebtListCreateView.as_view(), name='debt-list-create'),
    path('categories/', BudgetCategoryListCreateView.as_view(), name='category-list-create'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
]
