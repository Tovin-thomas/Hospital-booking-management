from django.urls import path
from . import views

urlpatterns = [
    path('booking', views.booking, name='booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('api/available-slots/', views.get_available_slots, name='get_available_slots'),
]

