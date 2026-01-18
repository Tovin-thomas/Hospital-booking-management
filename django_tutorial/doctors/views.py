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

@login_required
def doctor_dashboard(request):
    doctor = getattr(request.user, 'doctors', None)
    if not doctor:
        return render(request, '403.html', {'message': "Only doctors can access this page."})
    
    appointments = Booking.objects.filter(doc_name=doctor).order_by('booking_date')
    return render(request, 'doctors/dashboard.html', {
        'doctor': doctor,
        'appointments': appointments
    })

@login_required
def update_appointment_status(request, booking_id, status):
    doctor = getattr(request.user, 'doctors', None)
    booking = get_object_or_404(Booking, id=booking_id, doc_name=doctor)
    
    valid_statuses = [s[0] for s in Booking.STATUS_CHOICES]
    if status in valid_statuses:
        booking.status = status
        booking.save()
        messages.success(request, f"Appointment for {booking.p_name} marked as {status}.")
    
    return redirect('doctor_dashboard')

@login_required
def manage_schedule(request):
    doctor = getattr(request.user, 'doctors', None)
    if not doctor:
        return render(request, '403.html', {'message': "Only doctors can access this page."})
    
    availabilities = DoctorAvailability.objects.filter(doctor=doctor).order_by('day', 'start_time')
    leaves = DoctorLeave.objects.filter(doctor=doctor).order_by('date')
    
    if request.method == 'POST':
        if 'add_availability' in request.POST:
            a_form = AvailabilityForm(request.POST)
            if a_form.is_valid():
                avail = a_form.save(commit=False)
                avail.doctor = doctor
                avail.save()
                messages.success(request, "Availability added.")
                return redirect('manage_schedule')
        elif 'add_leave' in request.POST:
            l_form = LeaveForm(request.POST)
            if l_form.is_valid():
                leave = l_form.save(commit=False)
                leave.doctor = doctor
                leave.save()
                messages.success(request, "Leave added.")
                return redirect('manage_schedule')
    
    a_form = AvailabilityForm()
    l_form = LeaveForm()
    
    return render(request, 'doctors/manage_schedule.html', {
        'doctor': doctor,
        'availabilities': availabilities,
        'leaves': leaves,
        'a_form': a_form,
        'l_form': l_form,
    })

@login_required
def delete_availability(request, avail_id):
    doctor = getattr(request.user, 'doctors', None)
    avail = get_object_or_404(DoctorAvailability, id=avail_id, doctor=doctor)
    avail.delete()
    messages.info(request, "Availability removed.")
    return redirect('manage_schedule')
