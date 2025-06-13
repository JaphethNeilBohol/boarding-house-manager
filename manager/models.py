from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.core.validators import RegexValidator

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Room {self.room_number}"


class Tenant(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    ID_TYPE_CHOICES = [
        ('National ID', 'National ID'),
        ('Driver’s License', 'Driver’s License'),
        ('Passport', 'Passport'),
        ('Voter’s ID', 'Voter’s ID'),
        ('Student ID', 'Student ID'),
        ('Other', 'Other'),
    ]

    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?[\d\s\-]{7,15}$', message='Enter a valid phone number.')]
    )
    emergency_contact = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?[\d\s\-]{7,15}$', message='Enter a valid phone number.')]
    )
    address = models.CharField(max_length=255)
    id_type = models.CharField(max_length=50, choices=ID_TYPE_CHOICES)
    id_number = models.CharField(max_length=100)
    id_photo = models.ImageField(upload_to='tenant_ids/', null=True, blank=True)

    def __str__(self):
        return self.full_name


class Payment(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    month = models.CharField(max_length=15, choices=MONTH_CHOICES)
    year = models.IntegerField(default=datetime.now().year)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_bill = models.DecimalField(max_digits=10, decimal_places=2)
    water_bill = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.tenant.full_name} — {self.month} {self.year}"

class HistoryLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Added Tenant'),
        ('REMOVE', 'Removed Tenant'),
        ('UPDATE', 'Updated Info'),
        ('PAYMENT', 'Payment Recorded')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tenant_name = models.CharField(max_length=100)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_action_display()} - {self.tenant_name}"
