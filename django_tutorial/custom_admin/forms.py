from django import forms
from doctors.models import Doctors, Departments
from bookings.models import Booking

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = ['user', 'doc_name', 'doc_spec', 'dep_name', 'doc_image']
        widgets = {
            'doc_name': forms.TextInput(attrs={'class': 'form-control'}),
            'doc_spec': forms.TextInput(attrs={'class': 'form-control'}),
            'dep_name': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = ['dep_name', 'dep_decription']
        widgets = {
            'dep_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dep_decription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
