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
            # 0. Check if booking date is not in the past
            if date < datetime.date.today():
                self.add_error('booking_date', "Cannot book appointments for past dates. Please select today or a future date.")
                return cleaned_data
            
            # 1. Check for Doctor Leaves
            if DoctorLeave.objects.filter(doctor=doctor, date=date).exists():
                leave = DoctorLeave.objects.get(doctor=doctor, date=date)
                reason = f" (Reason: {leave.reason})" if leave.reason else ""
                self.add_error('booking_date', f"❌ Dr. {doctor.doc_name} is on leave on {date.strftime('%B %d, %Y')}{reason}. Please choose another date.")
                return cleaned_data
            
            # 2. Check for Weekly Availability (Is doctor working on this day?)
            day_of_week = date.weekday()  # Monday is 0, Sunday is 6
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day_of_week]
            availability_slots = DoctorAvailability.objects.filter(doctor=doctor, day=day_of_week)
            
            if not availability_slots.exists():
                self.add_error('booking_date', f"❌ Dr. {doctor.doc_name} is not available on {day_name}s. Please choose a different day.")
                
                # Show available days
                available_days = DoctorAvailability.objects.filter(doctor=doctor).values_list('day', flat=True).distinct()
                if available_days:
                    day_names = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][d] for d in available_days]
                    self.add_error('booking_date', f"ℹ️ Doctor is available on: {', '.join(day_names)}")
                return cleaned_data
            
            # 3. Check if Time Slot is within Doctor's Working Hours
            is_within_hours = False
            valid_slot = None
            for slot in availability_slots:
                if slot.start_time <= time <= slot.end_time:
                    is_within_hours = True
                    valid_slot = slot
                    break
            
            if not is_within_hours:
                # Show available time slots for this day
                slots_info = []
                for slot in availability_slots:
                    slots_info.append(f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}")
                
                self.add_error('appointment_time', 
                    f"❌ The selected time ({time.strftime('%I:%M %p')}) is outside Dr. {doctor.doc_name}'s working hours for {day_name}.")
                self.add_error('appointment_time', 
                    f"ℹ️ Available time slots: {' | '.join(slots_info)}")
                return cleaned_data
            
            # 4. Prevent Double Booking (Check if time slot is already taken)
            existing_bookings = Booking.objects.filter(
                doc_name=doctor, 
                booking_date=date, 
                appointment_time=time
            ).exclude(status__in=['rejected', 'cancelled'])
            
            if existing_bookings.exists():
                self.add_error('appointment_time', 
                    f"❌ This time slot ({time.strftime('%I:%M %p')} on {date.strftime('%B %d, %Y')}) is already booked by another patient.")
                self.add_error('appointment_time', 
                    "ℹ️ Please select a different time within the doctor's available hours.")
                return cleaned_data
                
        return cleaned_data
