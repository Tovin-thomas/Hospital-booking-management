from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Departments, Doctors, DoctorAvailability, DoctorLeave
from .forms import AvailabilityForm, LeaveForm
from bookings.models import Booking

def doctors(request):
    dict_docs = {
        'doctors': Doctors.objects.all().prefetch_related('availabilities', 'leaves')
    }
    return render(request, 'doctors.html', dict_docs)

def department(request):
    dict_dept={
        'dept': Departments.objects.all()
    }
    return render(request, 'department.html', dict_dept)


