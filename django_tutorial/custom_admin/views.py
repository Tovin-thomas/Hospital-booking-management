from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from doctors.models import Doctors, Departments
from bookings.models import Booking
from .forms import DoctorForm, DepartmentForm

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_doctors = Doctors.objects.count()
    total_bookings = Booking.objects.count()
    total_departments = Departments.objects.count()
    recent_bookings = Booking.objects.all().order_by('-booked_on')[:5]
    
    context = {
        'total_doctors': total_doctors,
        'total_bookings': total_bookings,
        'total_departments': total_departments,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'custom_admin/dashboard.html', context)

@user_passes_test(is_admin)
def manage_doctors(request):
    doctors = Doctors.objects.all()
    return render(request, 'custom_admin/manage_doctors.html', {'doctors': doctors})

@user_passes_test(is_admin)
def add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor added successfully!')
            return redirect('manage_doctors')
    else:
        form = DoctorForm()
    return render(request, 'custom_admin/doctor_form.html', {'form': form, 'title': 'Add Doctor'})

@user_passes_test(is_admin)
def edit_doctor(request, pk):
    doctor = get_object_or_404(Doctors, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor updated successfully!')
            return redirect('manage_doctors')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'custom_admin/doctor_form.html', {'form': form, 'title': 'Edit Doctor'})

@user_passes_test(is_admin)
def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctors, pk=pk)
    doctor.delete()
    messages.success(request, 'Doctor deleted successfully!')
    return redirect('manage_doctors')

@user_passes_test(is_admin)
def manage_departments(request):
    departments = Departments.objects.all()
    return render(request, 'custom_admin/manage_departments.html', {'departments': departments})

@user_passes_test(is_admin)
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('manage_departments')
    else:
        form = DepartmentForm()
    return render(request, 'custom_admin/department_form.html', {'form': form, 'title': 'Add Department'})

@user_passes_test(is_admin)
def edit_department(request, pk):
    department = get_object_or_404(Departments, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('manage_departments')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'custom_admin/department_form.html', {'form': form, 'title': 'Edit Department'})

@user_passes_test(is_admin)
def delete_department(request, pk):
    department = get_object_or_404(Departments, pk=pk)
    department.delete()
    messages.success(request, 'Department deleted successfully!')
    return redirect('manage_departments')

@user_passes_test(is_admin)
def manage_bookings(request):
    bookings = Booking.objects.all().order_by('-booked_on')
    return render(request, 'custom_admin/manage_bookings.html', {'bookings': bookings})

@user_passes_test(is_admin)
def update_booking_status(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = status
    booking.save()
    messages.success(request, f'Booking status updated to {status}!')
    return redirect('manage_bookings')
