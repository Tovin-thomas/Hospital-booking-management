from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookingForm

@login_required
def booking(request):
    # Redirect admins and doctors to their dashboard
    if request.user.is_superuser or hasattr(request.user, 'doctors'):
        return redirect('custom_admin_dashboard')
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'confirmation.html')
    form = BookingForm()
    dict_form={
        'form': form
    }
    return render(request, 'booking.html', dict_form)
