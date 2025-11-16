from django.db import models
from django.db import models
from users.models import CustomUser
from academics.models import Student 

class FeeStructure(models.Model):

    name = models.CharField(max_length=100, unique=True, help_text="e.g., Annual Tuition Fee, Term 1 Library Fee")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_required = models.BooleanField(default=True, help_text="Is this fee mandatory for all students?")
    academic_period = models.CharField(max_length=50, default='2024/2025 - Term 1')

    def __str__(self):
        return f"{self.name} ({self.amount})"

class Invoice(models.Model):
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    )

    # Link to the student who owes the money
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    
    invoice_number = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    fee_details = models.TextField(help_text="JSON representation of fee components.")

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.student}"

class Transaction(models.Model):
    
    METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Credit/Debit Card'),
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'profile__role': 'ACCOUNTANT'})

    # We can use UUID4 here for the external reference ID from the bank/payment gateway
    external_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="Unique ID for bank/external payment reference.")

    def __str__(self):
        return f"Payment of {self.amount_paid} on Invoice {self.invoice.invoice_number}"
