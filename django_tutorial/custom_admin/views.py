from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from doctors.models import Doctors, Departments, DoctorAvailability, DoctorLeave
from bookings.models import Booking
from core.models import Contact
from django.db.models import Q

def is_privileged(user):
    """Allow both superusers and doctors to access the dashboard"""
    return user.is_superuser or hasattr(user, 'doctors')

def is_superuser(user):
    """Only allow superusers for admin management"""
    return user.is_superuser

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
        return render(request, 'custom_admin/doctor/dashboard.html', context)
    else:
        # Superuser / Admin Dashboard Logic
        total_doctors = Doctors.objects.count()
        total_bookings = Booking.objects.count()
        total_departments = Departments.objects.count()
        total_messages = Contact.objects.count()
        unread_messages = Contact.objects.filter(is_read=False).count()
        recent_bookings = Booking.objects.all().order_by('-booked_on')[:5]
        recent_messages = Contact.objects.all()[:5]
        
        context = {
            'is_superuser': True,
            'total_doctors': total_doctors,
            'total_bookings': total_bookings,
            'total_departments': total_departments,
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'recent_bookings': recent_bookings,
            'recent_messages': recent_messages,
        }
    
        return render(request, 'custom_admin/dashboard.html', context)

# ============= DOCTOR MANAGEMENT =============

@user_passes_test(is_superuser)
def manage_doctors(request):
    """View all doctors with search functionality"""
    search_query = request.GET.get('search', '')
    
    if search_query:
        doctors = Doctors.objects.filter(
            Q(doc_name__icontains=search_query) | 
            Q(doc_spec__icontains=search_query) |
            Q(dep_name__dep_name__icontains=search_query)
        )
    else:
        doctors = Doctors.objects.all()
    
    context = {
        'doctors': doctors,
        'search_query': search_query,
    }
    return render(request, 'custom_admin/manage_doctors.html', context)

@user_passes_test(is_superuser)
def add_doctor(request):
    """Add a new doctor"""
    if request.method == 'POST':
        doc_name = request.POST.get('doc_name')
        doc_spec = request.POST.get('doc_spec')
        dep_name_id = request.POST.get('dep_name')
        doc_image = request.FILES.get('doc_image')
        
        # Optional: Create user account for doctor
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            department = Departments.objects.get(id=dep_name_id)
            
            # Create user if credentials provided
            user = None
            if username and email and password:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=doc_name
                )
            
            # Create doctor
            doctor = Doctors.objects.create(
                user=user,
                doc_name=doc_name,
                doc_spec=doc_spec,
                dep_name=department,
                doc_image=doc_image
            )
            
            messages.success(request, f'Doctor {doc_name} added successfully!')
            return redirect('manage_doctors')
        except Exception as e:
            messages.error(request, f'Error adding doctor: {str(e)}')
    
    departments = Departments.objects.all()
    context = {'departments': departments}
    return render(request, 'custom_admin/add_doctor.html', context)

@user_passes_test(is_superuser)
def edit_doctor(request, doctor_id):
    """Edit an existing doctor"""
    doctor = get_object_or_404(Doctors, id=doctor_id)
    
    if request.method == 'POST':
        doctor.doc_name = request.POST.get('doc_name')
        doctor.doc_spec = request.POST.get('doc_spec')
        dep_name_id = request.POST.get('dep_name')
        
        if request.FILES.get('doc_image'):
            doctor.doc_image = request.FILES.get('doc_image')
        
        # Handle user account creation/update
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        try:
            doctor.dep_name = Departments.objects.get(id=dep_name_id)
            
            # Determine if we should create/update user account
            if doctor.user:
                # Existing user - update if username or email provided
                if username or email:
                    if username:
                        doctor.user.username = username
                    if email:
                        doctor.user.email = email
                    if password:
                        doctor.user.set_password(password)
                    doctor.user.first_name = doctor.doc_name
                    doctor.user.save()
                    if password:
                        messages.success(request, f'✓ Doctor {doctor.doc_name} and user account "{doctor.user.username}" updated (password changed)!')
                    else:
                        messages.success(request, f'✓ Doctor {doctor.doc_name} and user account "{doctor.user.username}" updated!')
                else:
                    # Just update doctor info, no user changes
                    messages.success(request, f'✓ Doctor {doctor.doc_name} updated successfully!')
            else:
                # No existing user - create new if all three fields provided
                if username and email and password:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=doctor.doc_name
                    )
                    doctor.user = user
                    messages.success(request, f'✓ Doctor {doctor.doc_name} updated and user account "{username}" created successfully!')
                elif username or email or password:
                    # Partial credentials provided - warn user
                    messages.warning(request, '⚠️ To create a new user account, you must fill ALL three fields: username, email, AND password.')
                    messages.success(request, f'✓ Doctor {doctor.doc_name} updated successfully (no user account created)!')
                else:
                    messages.success(request, f'✓ Doctor {doctor.doc_name} updated successfully!')
            
            doctor.save()
            return redirect('manage_doctors')
        except Exception as e:
            messages.error(request, f'Error updating doctor: {str(e)}')
    
    departments = Departments.objects.all()
    users_without_doctors = User.objects.filter(doctors__isnull=True)
    context = {
        'doctor': doctor,
        'departments': departments,
        'selected_dept_id': doctor.dep_name_id,  # Pass ID directly to avoid template comparison issues
        'users_without_doctors': users_without_doctors,
    }
    return render(request, 'custom_admin/edit_doctor.html', context)

@user_passes_test(is_superuser)
def delete_doctor(request, doctor_id):
    """Delete a doctor"""
    doctor = get_object_or_404(Doctors, id=doctor_id)
    
    if request.method == 'POST':
        doctor_name = doctor.doc_name
        doctor.delete()
        messages.success(request, f'Doctor {doctor_name} deleted successfully!')
        return redirect('manage_doctors')
    
    context = {'doctor': doctor}
    return render(request, 'custom_admin/delete_doctor.html', context)

# ============= DEPARTMENT MANAGEMENT =============

@user_passes_test(is_superuser)
def manage_departments(request):
    """View all departments"""
    departments = Departments.objects.all()
    
    # Count doctors in each department
    for dept in departments:
        dept.doctor_count = Doctors.objects.filter(dep_name=dept).count()
    
    context = {'departments': departments}
    return render(request, 'custom_admin/manage_departments.html', context)

@user_passes_test(is_superuser)
def add_department(request):
    """Add a new department"""
    if request.method == 'POST':
        dep_name = request.POST.get('dep_name')
        dep_description = request.POST.get('dep_description')
        
        try:
            Departments.objects.create(
                dep_name=dep_name,
                dep_decription=dep_description
            )
            messages.success(request, f'Department {dep_name} added successfully!')
            return redirect('manage_departments')
        except Exception as e:
            messages.error(request, f'Error adding department: {str(e)}')
    
    return render(request, 'custom_admin/add_department.html')

@user_passes_test(is_superuser)
def edit_department(request, dept_id):
    """Edit an existing department"""
    department = get_object_or_404(Departments, id=dept_id)
    
    if request.method == 'POST':
        department.dep_name = request.POST.get('dep_name')
        department.dep_decription = request.POST.get('dep_description')
        
        try:
            department.save()
            messages.success(request, f'Department {department.dep_name} updated successfully!')
            return redirect('manage_departments')
        except Exception as e:
            messages.error(request, f'Error updating department: {str(e)}')
    
    context = {'department': department}
    return render(request, 'custom_admin/edit_department.html', context)

@user_passes_test(is_superuser)
def delete_department(request, dept_id):
    """Delete a department"""
    department = get_object_or_404(Departments, id=dept_id)
    
    if request.method == 'POST':
        dept_name = department.dep_name
        department.delete()
        messages.success(request, f'Department {dept_name} deleted successfully!')
        return redirect('manage_departments')
    
    context = {'department': department}
    return render(request, 'custom_admin/delete_department.html', context)

# ============= CONTACT MESSAGE MANAGEMENT =============

@user_passes_test(is_superuser)
def manage_messages(request):
    """View all contact messages"""
    messages_list = Contact.objects.all()
    
    context = {'messages_list': messages_list}
    return render(request, 'custom_admin/manage_messages.html', context)

@user_passes_test(is_superuser)
def view_message(request, message_id):
    """View a single contact message in detail"""
    message = get_object_or_404(Contact, id=message_id)
    
    # Mark as read when viewed
    if not message.is_read:
        message.is_read = True
        message.save()
    
    context = {'message': message}
    return render(request, 'custom_admin/view_message.html', context)

@user_passes_test(is_superuser)
def delete_message(request, message_id):
    """Delete a contact message"""
    message = get_object_or_404(Contact, id=message_id)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('manage_messages')
    
    context = {'message': message}
    return render(request, 'custom_admin/delete_message.html', context)

# ============= DOCTOR PORTAL FEATURES =============

def is_doctor(user):
    """Check if user is a doctor"""
    return hasattr(user, 'doctors')

@user_passes_test(is_doctor)
def my_appointments(request):
    """View for doctors to manage their appointments"""
    doctor = request.user.doctors
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    
    bookings = Booking.objects.filter(doc_name=doctor).order_by('-booked_on')
    
    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)
        
    context = {
        'bookings': bookings,
        'current_status': status_filter
    }
    return render(request, 'custom_admin/doctor/my_appointments.html', context)

@user_passes_test(is_doctor)
def update_booking_status(request, booking_id, new_status):
    """Update status of a specific booking"""
    booking = get_object_or_404(Booking, id=booking_id, doc_name=request.user.doctors)
    
    if new_status in ['accepted', 'rejected', 'completed']:
        booking.status = new_status
        booking.save()
        messages.success(request, f'Appointment marked as {new_status}.')
    
    return redirect('my_appointments')

@user_passes_test(is_doctor)
def schedule_management(request):
    """Manage doctor availability"""
    doctor = request.user.doctors
    
    if request.method == 'POST':
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:

            DoctorAvailability.objects.create(
                doctor=doctor,
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Availability slot added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding slot: {str(e)}')
            
    # Get availabilities ordered by day and time
    availabilities = doctor.availabilities.all().order_by('day', 'start_time')
    
    context = {
        'availabilities': availabilities,
        'days': DoctorAvailability.DAYS_OF_WEEK
    }
    return render(request, 'custom_admin/doctor/schedule_management.html', context)

@user_passes_test(is_doctor)
def delete_schedule(request, schedule_id):
    """Delete an availability slot"""
    from doctors.models import DoctorAvailability
    slot = get_object_or_404(DoctorAvailability, id=schedule_id, doctor=request.user.doctors)
    slot.delete()
    messages.success(request, 'Availability slot removed.')
    return redirect('schedule_management')

@user_passes_test(is_doctor)
def leave_management(request):
    """Manage leave requests"""
    doctor = request.user.doctors
    
    if request.method == 'POST':
        date = request.POST.get('date')
        reason = request.POST.get('reason')
        
        try:

            # Check if leave already exists for this date
            if DoctorLeave.objects.filter(doctor=doctor, date=date).exists():
                messages.warning(request, 'You already have a leave request for this date.')
            else:
                DoctorLeave.objects.create(
                    doctor=doctor,
                    date=date,
                    reason=reason
                )
                messages.success(request, 'Leave request submitted successfully.')
        except Exception as e:
            messages.error(request, f'Error submitting leave: {str(e)}')
            
    leaves = doctor.leaves.all().order_by('-date')
    
    context = {'leaves': leaves}
    return render(request, 'custom_admin/doctor/leave_management.html', context)

@user_passes_test(is_doctor)
def delete_leave(request, leave_id):
    """Cancel a leave request"""
    from doctors.models import DoctorLeave
    leave = get_object_or_404(DoctorLeave, id=leave_id, doctor=request.user.doctors)
    leave.delete()
    messages.success(request, 'Leave request cancelled.')
    return redirect('leave_management')
