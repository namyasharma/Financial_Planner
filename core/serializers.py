from rest_framework import serializers
from .models import Goal, Budget, Income, Expense, Debt, BudgetCategory, Notification
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}  # Prevent password from being returned

    def create(self, validated_data):
        user = User( 
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        user.set_password(validated_data["password"])  # Hash password before saving
        user.save()
        return user

class BudgetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = ['id', 'name', 'user']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'category', 'category_name', 'allocated_amount', 'spent_amount', 'remaining', 'user', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class GoalSerializer(serializers.ModelSerializer):
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Goal
        fields = ['id', 'name', 'target_amount', 'current_savings', 'remaining', 'due_date', 'user', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'amount', 'source', 'description', 'date', 'user', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class ExpenseSerializer(serializers.ModelSerializer):
    budget_name = serializers.CharField(source='budget.category.name', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'budget', 'budget_name', 'date', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'budget': {'required': True},
        }


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ['id', 'amount', 'creditor_name', 'description', 'due_date', 'user', 'created_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
