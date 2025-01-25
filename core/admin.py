from django.contrib import admin
from .models import Budget, Goal

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'allocated_amount', 'spent_amount', 'created_at']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'target_amount', 'current_savings', 'due_date', 'created_at']
