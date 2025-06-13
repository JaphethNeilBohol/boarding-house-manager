from django import forms
from .models import Tenant
from .models import Payment
from django.core.exceptions import ValidationError

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = [
            'full_name', 'age', 'gender', 'room',
            'move_in_date', 'move_out_date',
            'phone_number', 'emergency_contact', 'address',
            'id_type', 'id_number', 'id_photo',
        ]
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
            'move_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'full_name': 'Full Name (Last, First M.)',
            'emergency_contact': 'Emergency Contact Number',
            'address': 'Address (City/Barangay only)',
            'id_type': 'Valid ID Type',
            'id_number': 'ID Number',
            'id_photo': 'Upload ID Photo/Scan (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['tenant', 'month', 'year', 'rent_amount', 'electricity_bill', 'water_bill', 'paid_on']
        widgets = {
            'paid_on': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit tenant choices to active ones only
        self.fields['tenant'].queryset = Tenant.objects.filter(is_active=True)

        # Apply form-control class to all fields
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

