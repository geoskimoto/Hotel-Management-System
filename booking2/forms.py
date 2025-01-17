from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests']

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        guests = cleaned_data.get('guests')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        
         # Calculate stay duration
        if check_in and check_out:
            stay_duration = (check_out - check_in).days
            if stay_duration < room.min_stay:
                self.add_error('check_in', f"Minimum stay is {room.min_stay} nights.")
            if stay_duration > room.max_stay:
                self.add_error('check_in', f"Maximum stay is {room.max_stay} nights.")

        # Validate capacity.  Need to rename guests to like "occupants" or somethings since guest
        # has actual meaning and signficance in the app.
        if room and guests and guests > room.capacity:
            self.add_error('guests', f"Number of guests exceeds the room's capacity of {room.capacity}.")
        
        # Validate capacity across all rooms that are booked.    
        total_capacity = sum(room.capacity for room in self.rooms.all())
        if self.guests > total_capacity:
            raise ValidationError(f"The total capacity of selected rooms is {total_capacity}, but you are trying to book {self.guests} guests.")
        #
        if room and check_in and check_out:
            # Check for overlapping bookings in the room
            overlapping_bookings = Booking.objects.filter(room=room).filter(
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            if overlapping_bookings.exists():
                self.add_error('check_in', "This room is already booked for the selected dates.")

            # Validate booking window constraints
            if check_in < room.booking_window_start or check_out > room.booking_window_end:
                self.add_error('check_in', f"Booking must be within the allowed date range: {room.booking_window_start} to {room.booking_window_end}.")
            
            # Validate advance booking period (e.g., 7 days in advance)
            if check_in < timezone.now().date() + timezone.timedelta(days=0):
                self.add_error('check_in', "Bookings must be made at least 0 days in advance.")
            
            # Validate that checkout is after check-in
            if check_out <= check_in:
                self.add_error('check_in', "Check-out date must be after check-in date.")
     

        return cleaned_data
