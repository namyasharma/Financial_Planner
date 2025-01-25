from .models import Goal, Budget
from .serializers import GoalSerializer, BudgetSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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

class BulkGoalCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GoalSerializer(data=request.data, many=True)  # Set `many=True` for bulk data
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
