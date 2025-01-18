from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta


from django.db import models



class Room2(models.Model):
    name = models.CharField(max_length=255)
    room_type = models.CharField(default="bunk", max_length=255, blank=True, null=True)
    capacity = models.IntegerField()
    max_occupants = models.IntegerField(default=settings.DEFAULT_MAX_OCCUPANTS, blank=True, null=True)
    booking_window = models.IntegerField(default=settings.DEFAULT_BOOKING_WINDOW, help_text="Days in advance allowed for booking")
    
    def __str__(self):
        return self.name

    def clean(self):
        """
        Custom validation for room: Ensure max occupants does not exceed the global or room-specific limit.
        """
        if self.max_occupants is None:
            self.max_occupants = settings.DEFAULT_MAX_OCCUPANTS
        super().clean()

class Booking2(models.Model):
    room = models.ForeignKey(Room2, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    user = models.CharField(max_length=255)
    occupants = models.IntegerField()
    
    class Meta:
        unique_together = ['room', 'check_in', 'check_out']
    
    def __str__(self):
        return f"Booking for {self.room.name} from {self.check_in} to {self.check_out} by {self.user}"

    def clean(self):
        """
        Custom validations for booking: ensure room is available, dates are valid, occupancy is within limits.
        """
        # Booking must not overlap
        if Booking2.objects.filter(room=self.room, check_in__lt=self.check_out, check_out__gt=self.check_in).exists():
            raise ValidationError(f"The room {self.room.name} is already booked for these dates.")

        # Check against blocked dates for the room
        if BlockedDate.objects.filter(room=self.room, start_date__lt=self.check_out, end_date__gt=self.check_in).exists():
            raise ValidationError(f"The room {self.room.name} is blocked for these dates.")
        
        if BlockedDate.objects.filter(room=None, start_date__lt=self.check_out, end_date__gt=self.check_in).exists():
            raise ValidationError("These dates are globally blocked for all rooms.")

        # Ensure check-out is after check-in
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")
        
        # Ensure booking dates are not in the past
        if self.check_in < settings.MIN_BOOKING_DATE:
            raise ValidationError("Booking cannot be made for past dates.")
        
        # Ensure booking stays are within the allowed duration window
        booking_duration = self.check_out - self.check_in
        if booking_duration < timedelta(days=settings.MIN_STAY_DAYS):
            raise ValidationError(f"Stay must be at least {settings.MIN_STAY_DAYS} days.")
        
        if booking_duration > timedelta(days=settings.MAX_STAY_DAYS):
            raise ValidationError(f"Stay cannot exceed {settings.MAX_STAY_DAYS} days.")
        
        # Ensure the number of occupants is within the room's capacity
        if self.occupants > self.room.max_occupants:
            raise ValidationError(f"Room capacity exceeded. Maximum occupants: {self.room.max_occupants}.")
        
        super().clean()

    @staticmethod
    def book_room(room_id, check_in, check_out, user, occupants):
        """
        Perform the booking operation while ensuring no overlap and locking the room.
        """
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Lock the room for update to prevent other bookings
                room = Room2.objects.select_for_update().get(id=room_id)
                
                # Perform all the validations using the room's and global settings
                booking = Booking2(room=room, check_in=check_in, check_out=check_out, user=user, occupants=occupants)
                booking.full_clean()  # Call clean() to run all custom validations
                
                # Create the booking
                booking.save()
                return booking
        except Room2.DoesNotExist:
            raise ValidationError("Room does not exist.")
        except Exception as e:
            raise ValidationError(f"Booking failed: {e}")


class BlockedDate(models.Model):
    room = models.ForeignKey(Room2, on_delete=models.CASCADE, related_name='blocked_dates')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200)

    def __str__(self):
        return f"Blocked from {self.start_date} to {self.end_date} for {self.reason}"
