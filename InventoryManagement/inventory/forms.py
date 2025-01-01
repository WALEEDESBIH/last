from django import forms
from .models import Stock


class CreateStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'vocab_no',
            'name',
            'description1',
            'description2',
            'unit',
            'unit_cost',
            'category',
            'image',
            'inventory',
        ]
        widgets = {
            'description1': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter description'}),
            'description2': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter additional description'}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter unit cost'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class UpdateStockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'vocab_no',
            'name',
            'description1',
            'description2',
            'unit',
            'unit_cost',
            'category',
            'image',
            'threshold',
            'source',
            'image',

        ]
        widgets = {
            'description1': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter description'}),
            'description2': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter additional description'}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Enter unit cost'}),
            'threshold': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Enter stock threshold'}),
            'source': forms.TextInput(attrs={'placeholder': 'Enter source'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

