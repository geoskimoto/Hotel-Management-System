from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Booking2
from .forms import BookingForm
from django.core.exceptions import ValidationError

def book_room(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                room = form.cleaned_data['room']
                check_in = form.cleaned_data['check_in']
                check_out = form.cleaned_data['check_out']
                user = form.cleaned_data['user']
                occupants = form.cleaned_data['occupants']
                
                # Try to make the booking using the model's static method
                booking = Booking2.book_room(room.id, check_in, check_out, user, occupants)
                messages.success(request, f"Room {room.name} booked successfully!")
                return redirect('booking_confirmation', booking_id=booking.id)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('book_room')
    
    else:
        form = BookingForm()

    return render(request, 'booking/book_room.html', {'form': form})

def booking_confirmation(request, booking_id):
    try:
        booking = Booking2.objects.get(id=booking_id)
        return render(request, 'booking/booking_confirmation.html', {'booking': booking})
    except Booking2.DoesNotExist:
        return HttpResponse("Booking not found", status=404)
