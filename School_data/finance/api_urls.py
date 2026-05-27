from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    FeeCategoryViewSet, FeeStructureViewSet, StudentFeeViewSet,
    PaymentViewSet, ExpenseCategoryViewSet, ExpenseViewSet,
    ScholarshipViewSet, finance_summary
)

app_name = 'finance_api'

router = DefaultRouter()
router.register(r'fee-categories', FeeCategoryViewSet)
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'student-fees', StudentFeeViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'scholarships', ScholarshipViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', finance_summary, name='finance_summary'),
]
