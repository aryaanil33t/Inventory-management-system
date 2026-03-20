from django import forms
from .models import Rack, Warehouse

class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        fields = ['name', 'capacity', 'warehouse']  # exclude active_status
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter rack name'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter capacity'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
        }