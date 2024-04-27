from django import forms
from .models import Address, Category, FoodProduct, Supplier
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import TextInput, NumberInput, Textarea, Select

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'is_active', 'parent', 'pnd_location', 'weight_limit']
        labels = {
            'name': 'Category Name',
            'slug': 'Category Slug',
            'is_active': 'Is Active',
            'parent': 'Parent Category',
            'pnd_location': 'PND Location',
            'weight_limit': 'Weight Limit (kg)'
        }
        help_texts = {
            'name': 'Required. Maximum 100 characters.',
            'slug': 'Required. Letters, numbers, underscore, or hyphens.',
            'is_active': 'Check to mark category as active.',
            'parent': 'Optional. Select a parent category if applicable.',
            'pnd_location': 'Preferred PND location for this category.',
            'weight_limit': 'Maximum weight limit for this category in kilograms.'
        }
        widgets = {
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'pnd_location': forms.Select(attrs={'class': 'form-control'}),
            'weight_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class FoodProductForm(forms.ModelForm):
    class Meta:
        model = FoodProduct
        fields = ['sku', 'name', 'description', 'quantity', 'unit_price', 'category', 'suppliers', 'is_high_demand', 'batch_number', 'storage_temperature', 'date_received', 'expiration_date', 'supplier', 'last_updated_by']
        widgets = {
            'sku': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter SKU'}),
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
            'quantity': NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'unit_price': NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': Select(attrs={'class': 'form-control'}),
            'suppliers': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_high_demand': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'batch_number': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter batch number'}),
            'storage_temperature': TextInput(attrs={'class': 'form-control', 'placeholder': 'Storage Temperature'}),
            'date_received': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter supplier name'}),
            'last_updated_by': Select(attrs={'class': 'form-control'}),
        }
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_number', 'street_name', 'city', 'county', 'country', 'post_code']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact', 'email', 'contact_number', 'address']
        widgets = {
            'address': forms.HiddenInput()  
        }
        


