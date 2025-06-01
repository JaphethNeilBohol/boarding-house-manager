from django import forms
from .models import Boarder

class BoarderForm(forms.ModelForm):
    class Meta:
        model = Boarder
        fields = ['name', 'room_number', 'contact', 'move_in_date']