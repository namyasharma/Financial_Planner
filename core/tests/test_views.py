from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from core.models import Goal, Budget, Income, Expense, Debt, BudgetCategory, Notification

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.token = self.client.post("/api/token/", {"username": "testuser", "password": "testpass"}).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_budget_list_create(self):
        category = BudgetCategory.objects.create(user=self.user, name="Food")
        
        # Test POST with Decimal values
        response = self.client.post("/budget/", {"category": category.id, "allocated_amount": str(Decimal("1000.00"))})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category_name"], "Food")

        # Test GET
        response = self.client.get("/budget/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_goal_list_create(self):
        # Test POST with Decimal values
        response = self.client.post("/goals/", {"name": "Car", "target_amount": str(Decimal("5000.00")), "due_date": "2025-12-31"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Car")

        # Test GET
        response = self.client.get("/goals/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_bulk_goal_create(self):
        goals = [
            {"name": "House", "target_amount": str(Decimal("10000.00")), "due_date": "2025-12-31"},
            {"name": "Vacation", "target_amount": str(Decimal("3000.00")), "due_date": "2025-06-30"},
        ]
        response = self.client.post("/goals/bulk-create/", goals, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

    def test_spending_summary(self):
        category = BudgetCategory.objects.create(user=self.user, name="Food")
        budget = Budget.objects.create(user=self.user, category=category, allocated_amount=Decimal("1000.00"), spent_amount=Decimal("200.00"))
        
        response = self.client.get("/spending-summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["remaining_budget"], Decimal("800.00"))

    def test_income_list_create(self):
        # Test POST with Decimal values
        response = self.client.post("/income/", {"amount": str(Decimal("3000.00")), "source": "Salary", "date": "2025-01-01"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["source"], "Salary")

        # Test GET
        response = self.client.get("/income/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_expense_list_create(self):
        category = BudgetCategory.objects.create(user=self.user, name="Food")
        budget = Budget.objects.create(user=self.user, category=category, allocated_amount=Decimal("1000.00"))
        
        # Test POST with Decimal values
        response = self.client.post(
            "/expenses/",
            {"budget": budget.id, "amount": str(Decimal("200.00")), "description": "Groceries", "date": "2025-01-01"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["description"], "Groceries")

    def test_debt_list_create(self):
        # Test POST with Decimal values
        response = self.client.post("/debts/", {"amount": str(Decimal("1000.00")), "creditor_name": "Bank", "due_date": "2025-12-31"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["creditor_name"], "Bank")

        # Test GET
        response = self.client.get("/debts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_budget_category_list_create(self):
        # Test POST
        response = self.client.post("/categories/", {"name": "Travel"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Travel")

        # Test GET
        response = self.client.get("/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_notifications(self):
        Notification.objects.create(user=self.user, message="New goal created")
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
