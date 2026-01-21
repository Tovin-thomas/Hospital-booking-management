from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact

def index(request):
    # Redirect logged-in doctors and admins to their dashboards
    if request.user.is_authenticated:
        if request.user.is_superuser or hasattr(request.user, 'doctors'):
            return redirect('custom_admin_dashboard')
    
    # Homepage accessible to everyone else (public or regular users)
    return render(request, 'index.html')
    
def about(request):
    # Redirect logged-in doctors and admins to their dashboards
    if request.user.is_authenticated:
        if request.user.is_superuser or hasattr(request.user, 'doctors'):
            return redirect('custom_admin_dashboard')
    
    return render(request, 'about.html')

def contact(request):
    # Redirect logged-in doctors and admins to their dashboards
    if request.user.is_authenticated:
        if request.user.is_superuser or hasattr(request.user, 'doctors'):
            return redirect('custom_admin_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate fields
        if name and email and subject and message:
            # Save contact message
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'contact.html')
