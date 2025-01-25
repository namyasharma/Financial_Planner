from rest_framework import serializers
from .models import Budget, Goal

class BudgetSerializer(serializers.ModelSerializer):
    remaining = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = ['id', 'category', 'allocated_amount', 'spent_amount', 'remaining', 'created_at']

class GoalSerializer(serializers.ModelSerializer):
    remaining = serializers.ReadOnlyField()

    class Meta:
        model = Goal
        fields = ['id', 'name', 'target_amount', 'current_savings', 'remaining', 'due_date', 'created_at']
