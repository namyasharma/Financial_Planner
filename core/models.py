from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.allocated_amount - self.spent_amount

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def remaining(self):
        return self.target_amount - self.current_savings
