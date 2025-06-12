from django import forms
from .models import Orders

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['name', 'address', 'city', 'state', 'pincode', 'phoneno']
        labels = {
            'name': 'Full Name',
            'address': 'Street Address',
            'city': 'City',
            'state': 'State',
            'pincode': 'PIN Code',
            'phoneno': 'Phone Number',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your complete address',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
            }),
            'pincode': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'PIN Code',
            }),
            'phoneno': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }),
        }