from .models import Goal, Budget, Income, Expense, Debt, BudgetCategory, Notification
from .serializers import UserSerializer
from .serializers import GoalSerializer, BudgetSerializer, IncomeSerializer, ExpenseSerializer, DebtSerializer, BudgetCategorySerializer
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework import viewsets
from datetime import datetime, timezone


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if User.objects.filter(username=request.data["username"]).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            refresh = RefreshToken.for_user(user)
            print(refresh)
            return Response({
                 "access": str(refresh.access_token),
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                "refresh": str(refresh),
                "access": str(access_token),
                "access_expires_at": datetime.now(timezone.utc) + refresh.access_token.lifetime,
                "refresh_expires_at": datetime.now(timezone.utc) + refresh.lifetime
            }, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
     
      
class GoalListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = Goal.objects.filter(user=request.user)
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GoalUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, goal_id):
        goal = Goal.objects.filter(id=goal_id, user=request.user).first()
        if not goal:
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, goal_id):
        goal = Goal.objects.filter(id=goal_id, user=request.user).first()
        if not goal:
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        progress = request.data.get("progress")
        if progress is None:
            return Response({"error": "Progress value is required"}, status=status.HTTP_400_BAD_REQUEST)

        goal.progress = progress
        goal.save()
        return Response({"message": "Goal progress updated successfully"}, status=status.HTTP_200_OK)


class GoalPriorityUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, goal_id):
        goal = Goal.objects.filter(id=goal_id, user=request.user).first()
        if not goal:
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        priority = request.data.get("priority")
        if priority is None:
            return Response({"error": "Priority value is required"}, status=status.HTTP_400_BAD_REQUEST)

        goal.priority = priority
        goal.save()
        return Response({"message": "Goal priority updated successfully"}, status=status.HTTP_200_OK)


class BulkGoalCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoalSerializer(data=request.data, many=True)  # many=True to handle list of goals
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BudgetListCreateView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        budgets = Budget.objects.filter(user=request.user)
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetAllocationView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, budget_id):
        budget = Budget.objects.filter(id=budget_id, user=request.user).first()
        if not budget:
            return Response({"error": "Budget not found"}, status=status.HTTP_404_NOT_FOUND)

        allocated_amount = request.data.get("allocated_amount")
        if allocated_amount is not None:
            budget.allocated_amount = allocated_amount
            budget.save()
            return Response({"message": "Budget updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Allocated amount required"}, status=status.HTTP_400_BAD_REQUEST)


class SpendingSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        budgets = Budget.objects.filter(user=request.user)
        total_allocated = sum(budget.allocated_amount for budget in budgets)
        total_spent = sum(budget.spent_amount for budget in budgets)
        remaining_budget = total_allocated - total_spent

        summary = {
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "remaining_budget": remaining_budget
        }
        return Response(summary, status=status.HTTP_200_OK)


class IncomeExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_income = Income.objects.filter(user=request.user).aggregate(total_income=Sum('amount'))['total_income'] or 0
        total_expense = Expense.objects.filter(budget__user=request.user).aggregate(total_expense=Sum('amount'))['total_expense'] or 0
        balance = total_income - total_expense

        summary = {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        }
        return Response(summary, status=status.HTTP_200_OK)


class IncomeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        incomes = Income.objects.filter(user=request.user)
        serializer = IncomeSerializer(incomes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = IncomeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.filter(budget__user=request.user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkExpenseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DebtListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        debts = Debt.objects.filter(user=request.user)
        serializer = DebtSerializer(debts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DebtSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DebtPayoffView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, debt_id):
        debt = Debt.objects.filter(id=debt_id, user=request.user).first()
        if not debt:
            return Response({"error": "Debt not found"}, status=status.HTTP_404_NOT_FOUND)

        debt.paid_off = True
        debt.save()
        return Response({"message": "Debt marked as paid off"}, status=status.HTTP_200_OK)


class DebtSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_debt = Debt.objects.filter(user=request.user).aggregate(total_debt=Sum('amount'))['total_debt'] or 0
        total_paid = Debt.objects.filter(user=request.user, paid_off=True).aggregate(total_paid=Sum('amount'))['total_paid'] or 0
        remaining_debt = total_debt - total_paid

        summary = {
            "total_debt": total_debt,
            "total_paid": total_paid,
            "remaining_debt": remaining_debt
        }
        return Response(summary, status=status.HTTP_200_OK)


class BudgetCategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = BudgetCategory.objects.filter(user=request.user)
        serializer = BudgetCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BudgetCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetCategoryUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, category_id):
        category = BudgetCategory.objects.filter(id=category_id, user=request.user).first()
        if not category:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BudgetCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        data = [{"id": n.id, "message": n.message, "created_at": n.created_at} for n in notifications]
        return Response(data, status=status.HTTP_200_OK)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        notification_ids = request.data.get("ids", [])
        if not notification_ids:
            return Response({"error": "No notification IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        notifications = Notification.objects.filter(id__in=notification_ids, user=request.user, is_read=False)
        if notifications.exists():
            notifications.update(is_read=True)
            return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
        return Response({"error": "No notifications found to mark as read"}, status=status.HTTP_404_NOT_FOUND)
