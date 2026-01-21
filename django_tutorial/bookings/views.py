from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import BookingForm
from doctors.models import DoctorAvailability, DoctorLeave, Doctors
from .models import Booking
import datetime

@login_required
def booking(request):
    # Redirect admins and doctors to their dashboard
    if request.user.is_superuser or hasattr(request.user, 'doctors'):
        return redirect('custom_admin_dashboard')
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_instance = form.save(commit=False)
            booking_instance.user = request.user  # Link booking to current user
            booking_instance.save()
            messages.success(request, f'✅ Appointment booked successfully with Dr. {booking_instance.doc_name.doc_name} on {booking_instance.booking_date.strftime("%B %d, %Y")} at {booking_instance.appointment_time.strftime("%I:%M %p")}!')
            return render(request, 'confirmation.html')
    else:
        form = BookingForm()
    
    dict_form = {
        'form': form
    }
    return render(request, 'booking.html', dict_form)

@login_required
def get_available_slots(request):
    """AJAX endpoint to get available time slots for a doctor on a specific date"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        doctor = Doctors.objects.get(id=doctor_id)
        booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Check if date is in the past
        if booking_date < datetime.date.today():
            return JsonResponse({
                'available': False,
                'message': 'Cannot book for past dates'
            })
        
        # Check if doctor is on leave
        if DoctorLeave.objects.filter(doctor=doctor, date=booking_date).exists():
            leave = DoctorLeave.objects.get(doctor=doctor, date=booking_date)
            return JsonResponse({
                'available': False,
                'message': f'Dr. {doctor.doc_name} is on leave on this date' + (f': {leave.reason}' if leave.reason else '')
            })
        
        # Get availability for the day
        day_of_week = booking_date.weekday()
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]
        availability_slots = DoctorAvailability.objects.filter(doctor=doctor, day=day_of_week)
        
        if not availability_slots.exists():
            # Get available days
            available_days = DoctorAvailability.objects.filter(doctor=doctor).values_list('day', flat=True).distinct()
            day_names = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][d] for d in available_days]
            
            return JsonResponse({
                'available': False,
                'message': f'Dr. {doctor.doc_name} is not available on {day_name}s',
                'available_days': day_names
            })
        
        # Get booked time slots
        booked_times = list(Booking.objects.filter(
            doc_name=doctor,
            booking_date=booking_date
        ).exclude(status__in=['rejected', 'cancelled']).values_list('appointment_time', flat=True))
        
        # Format booked times as strings
        booked_times_str = [t.strftime('%H:%M') for t in booked_times]
        
        # Format available slots
        slots = []
        for slot in availability_slots:
            slots.append({
                'start': slot.start_time.strftime('%H:%M'),
                'end': slot.end_time.strftime('%H:%M'),
                'display': f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            })
        
        return JsonResponse({
            'available': True,
            'slots': slots,
            'booked_times': booked_times_str,
            'message': f'Dr. {doctor.doc_name} is available on {day_name}'
        })
        
    except Doctors.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

@login_required
def my_bookings(request):
    """View for users to see their booking history"""
    # Redirect admins and doctors to their dashboard
    if request.user.is_superuser or hasattr(request.user, 'doctors'):
        return redirect('custom_admin_dashboard')
    
    # Get all bookings for current user
    bookings = Booking.objects.filter(user=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
    
    # Search by doctor name or date
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        bookings = bookings.filter(
            Q(doc_name__doc_name__icontains=search_query) |
            Q(doc_name__doc_spec__icontains=search_query)
        )
    
    # Order by booking date (upcoming first, then past)
    bookings = bookings.order_by('-booking_date', '-appointment_time')
    
    # Count statistics
    total_count = Booking.objects.filter(user=request.user).count()
    pending_count = Booking.objects.filter(user=request.user, status='pending').count()
    accepted_count = Booking.objects.filter(user=request.user, status='accepted').count()
    completed_count = Booking.objects.filter(user=request.user, status='completed').count()
    cancelled_count = Booking.objects.filter(user=request.user, status='cancelled').count()
    
    context = {
        'bookings': bookings,
        'current_status': status_filter,
        'search_query': search_query,
        'total_count': total_count,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'my_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Allow users to cancel their bookings"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow cancellation of pending or accepted bookings
    if booking.status in ['pending', 'accepted']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f'✅ Your appointment with Dr. {booking.doc_name.doc_name} on {booking.booking_date.strftime("%B %d, %Y")} has been cancelled.')
    else:
        messages.error(request, f'❌ Cannot cancel this appointment (Status: {booking.get_status_display()}).')
    
    return redirect('my_bookings')


