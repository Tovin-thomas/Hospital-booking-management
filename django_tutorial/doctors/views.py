from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Departments, Doctors, DoctorAvailability, DoctorLeave
from .forms import AvailabilityForm, LeaveForm
from bookings.models import Booking

def doctors(request):
    # Get department filter from URL parameter
    department_id = request.GET.get('department', None)
    selected_department = None
    
    # Filter doctors by department if specified
    if department_id:
        doctors_list = Doctors.objects.filter(dep_name_id=department_id).prefetch_related('availabilities', 'leaves')
        selected_department = get_object_or_404(Departments, id=department_id)
    else:
        doctors_list = Doctors.objects.all().prefetch_related('availabilities', 'leaves')
    
    dict_docs = {
        'doctors': doctors_list,
        'selected_department': selected_department,
        'all_departments': Departments.objects.all(),
    }
    return render(request, 'doctors.html', dict_docs)

def department(request):
    dict_dept={
        'dept': Departments.objects.all()
    }
    return render(request, 'department.html', dict_dept)


