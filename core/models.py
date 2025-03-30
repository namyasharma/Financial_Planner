from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


def default_end_date():
    return date.today() + timedelta(days=30)

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    currency_preference = models.CharField(max_length=10, default="USD")

    def __str__(self):
        return self.username

class BudgetCategory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Income(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="incomes")
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    recurring = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - ${self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name="budgets")
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=default_end_date)
    is_recurring = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(CustomUser, related_name="shared_budgets", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.allocated_amount - self.spent_amount

    def __str__(self):
        return f"{self.category.name}: {self.start_date} to {self.end_date}"


class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="expenses")
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - ${self.amount}"


class Goal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="goals")
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.target_amount - self.current_savings

    def __str__(self):
        return f"{self.name} - Target: ${self.target_amount}, Due: {self.due_date}"


class Debt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="debts")
    creditor_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    description = models.TextField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return f"Debt to {self.creditor_name} - ${self.amount}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
