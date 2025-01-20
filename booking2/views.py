from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Booking2, Room2
from .forms import BookingForm
from django.core.exceptions import ValidationError



#--------------booking functions that don't use sessions---------------
# def book_room(request):
#     if request.method == 'POST':
#         form = BookingForm(request.POST)
#         if form.is_valid():
#             try:
#                 room = form.cleaned_data['room']
#                 check_in = form.cleaned_data['check_in']
#                 check_out = form.cleaned_data['check_out']
#                 user = form.cleaned_data['user']
#                 occupants = form.cleaned_data['occupants']
                
#                 # Try to make the booking using the model's static method
#                 booking = Booking2.book_room(room.id, check_in, check_out, user, occupants)
#                 messages.success(request, f"Room {room.name} booked successfully!")
#                 return redirect('booking2/booking_confirmation', booking_id=booking.id)
#             except ValidationError as e:
#                 messages.error(request, str(e))
#                 return redirect('booking2/book_room')
    
#     else:
#         form = BookingForm()

#     return render(request, 'booking2/book_room.html', {'form': form})

# def booking_confirmation(request, booking_id):
#     try:
#         booking = Booking2.objects.get(id=booking_id)
#         return render(request, 'booking2/booking_confirmation.html', {'booking': booking})
#     except Booking2.DoesNotExist:
#         return HttpResponse("Booking not found", status=404)


#---------------Booking functions that do use sessions-------------------

def book_room(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Save form data in session
            request.session['booking_data'] = form.cleaned_data
            return redirect('booking2/booking_confirmation')
    else:
        form = BookingForm()

    return render(request, 'booking2/book_room.html', {'form': form})

def booking_confirmation(request):
    booking_data = request.session.get('booking_data')
    if not booking_data:
        return HttpResponse("No booking data available.")

    room = Room2.objects.get(id=booking_data['room'])
    return render(request, 'booking2/booking_confirmation.html', {
        'room': room,
        'check_in': booking_data['check_in'],
        'check_out': booking_data['check_out'],
        'occupants': booking_data['occupants'],
    })
    
#This function deletes session data after booking is confirmed.
def confirm_booking(request):
    booking_data = request.session.pop('booking_data', None)
    if not booking_data:
        return HttpResponse("No booking data to confirm.")

    room = Room.objects.get(id=booking_data['room'])
    Booking2.objects.create(
        room=room,
        check_in=booking_data['check_in'],
        check_out=booking_data['check_out'],
        occupants=booking_data['occupants'],
        user=request.user
    )
    return HttpResponse("Booking confirmed!")
