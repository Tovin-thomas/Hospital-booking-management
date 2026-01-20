from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from doctors.models import Doctors, Departments
from bookings.models import Booking
from core.models import Contact
from .forms import DoctorForm, DepartmentForm

def is_admin(user):
    return user.is_superuser

def is_privileged(user):
    return user.is_superuser or hasattr(user, 'doctors')

@user_passes_test(is_privileged)
def admin_dashboard(request):
    if hasattr(request.user, 'doctors'):
        # Doctor Dashboard Logic
        doctor = request.user.doctors
        # Counts specific to the doctor
        total_bookings = Booking.objects.filter(doc_name=doctor).count()
        pending_bookings = Booking.objects.filter(doc_name=doctor, status='pending').count()
        completed_bookings = Booking.objects.filter(doc_name=doctor, status='completed').count()
        
        # Recent bookings for this doctor only
        recent_bookings = Booking.objects.filter(doc_name=doctor).order_by('-booked_on')[:5]
        
        context = {
            'is_doctor': True,
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'completed_bookings': completed_bookings,
            'recent_bookings': recent_bookings,
        }
    else:
        # Superuser / Admin Dashboard Logic
        total_doctors = Doctors.objects.count()
        total_bookings = Booking.objects.count()
        total_departments = Departments.objects.count()
        recent_bookings = Booking.objects.all().order_by('-booked_on')[:5]
        
        context = {
            'is_superuser': True,
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

@user_passes_test(is_privileged)
def manage_bookings(request):
    if hasattr(request.user, 'doctors'):
        bookings = Booking.objects.filter(doc_name=request.user.doctors).order_by('-booked_on')
    else:
        bookings = Booking.objects.all().order_by('-booked_on')
    return render(request, 'custom_admin/manage_bookings.html', {'bookings': bookings})

@user_passes_test(is_privileged)
def update_booking_status(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Security check: Ensure doctors modify only their own bookings
    if hasattr(request.user, 'doctors') and booking.doc_name != request.user.doctors:
        messages.error(request, "You are not authorized to update this booking.")
        return redirect('manage_bookings')
        
    booking.status = status
    booking.save()
    messages.success(request, f'Booking status updated to {status}!')
    return redirect('manage_bookings')

@user_passes_test(is_admin)
def manage_contacts(request):
    contacts = Contact.objects.all().order_by('-submitted_at')
    unread_count = Contact.objects.filter(is_read=False).count()
    return render(request, 'custom_admin/manage_contacts.html', {
        'contacts': contacts,
        'unread_count': unread_count
    })

@user_passes_test(is_admin)
def view_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    # Mark as read when viewed
    if not contact.is_read:
        contact.is_read = True
        contact.save()
    return render(request, 'custom_admin/view_contact.html', {'contact': contact})

@user_passes_test(is_admin)
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    messages.success(request, 'Contact message deleted successfully!')
    return redirect('manage_contacts')

