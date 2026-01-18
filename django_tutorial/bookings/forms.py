from django import forms
from .models import Booking
from doctors.models import DoctorAvailability, DoctorLeave
import datetime

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['p_name', 'p_phone', 'p_email', 'doc_name', 'booking_date', 'appointment_time']
        widgets = {
            'booking_date': DateInput(attrs={'class': 'form-control'}),
            'appointment_time': TimeInput(attrs={'class': 'form-control'}),
            'p_name': forms.TextInput(attrs={'class': 'form-control'}),
            'p_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'p_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'doc_name': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
           'p_name':'Patient Name',
           'p_phone':'Phone Number',
           'p_email':'Email',
           'doc_name':'Doctor Name',
           'booking_date':'Booking Date',
           'appointment_time': 'Appointment Time'
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doc_name')
        date = cleaned_data.get('booking_date')
        time = cleaned_data.get('appointment_time')

        if doctor and date and time:
            # 1. Check for Leaves
            if DoctorLeave.objects.filter(doctor=doctor, date=date).exists():
                self.add_error('booking_date', f"Dr. {doctor.doc_name} is on leave on this date.")
            
            # 2. Check for Weekly Availability
            day_of_week = date.weekday() # Monday is 0
            availability = DoctorAvailability.objects.filter(doctor=doctor, day=day_of_week)
            
            if not availability.exists():
                self.add_error('booking_date', f"Dr. {doctor.doc_name} is not available on {date.strftime('%A')}s.")
            else:
                # 3. Check Time Slot within Availability
                is_within_hours = False
                for slot in availability:
                    if slot.start_time <= time <= slot.end_time:
                        is_within_hours = True
                        break
                
                if not is_within_hours:
                    self.add_error('appointment_time', f"Requested time is outside Dr. {doctor.doc_name}'s working hours.")
            
            # 4. Prevent Overbooking
            if Booking.objects.filter(doc_name=doctor, booking_date=date, appointment_time=time).exclude(status__in=['rejected', 'cancelled']).exists():
                self.add_error('appointment_time', "This exact time slot is already booked. Please choose another time.")
                
        return cleaned_data
