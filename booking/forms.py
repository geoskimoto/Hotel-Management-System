from django import forms
from hotel.models import Booking, BlockedDate
from django.core.exceptions import ValidationError
from datetime import date

# ROOM_TYPES = [
#     ('single', 'Single'),
#     ('double', 'Double'),
#     ('suite', 'Suite'),
# ]
#
# class AvailabilityForm(forms.Form):
#     check_in = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     check_out = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     guests = forms.IntegerField(min_value=1)
#     room_type = forms.ChoiceField(choices=ROOM_TYPES)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         check_in = cleaned_data.get('check_in')
#         check_out = cleaned_data.get('check_out')
#         if check_in and check_out and check_in >= check_out:
#             raise forms.ValidationError("Check-out date must be after check-in date.")
#         if check_in and check_in < date.today():
#             raise forms.ValidationError("Check-in date cannot be in the past.")
#         return cleaned_data







class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'room_type', 'check_in_date', 'check_out_date', 'num_members', 'num_children', 'num_guests', ]

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        # occupants = cleaned_data.get('occupants')
        
        # Ensure check-out is after check-in
        if check_in and check_out and check_out <= check_in:
            raise ValidationError("Check-out date must be after check-in date.")

        # Ensure the booking is within the allowed window
        booking_window = room.booking_window
        today = date.today()
        if check_in < today:
            raise ValidationError("Booking cannot be made for past dates.")
        
        if (check_in - today).days > booking_window:
            raise ValidationError(f"Bookings can only be made within {booking_window} days in advance.")

        if BlockedDate.objects.filter(room=room, start_date__lt=check_out, end_date__gt=check_in).exists():
            raise ValidationError(f"The room {room.name} is blocked for these dates.")
        
        if BlockedDate.objects.filter(room=None, start_date__lt=check_out, end_date__gt=check_in).exists():
            raise ValidationError("These dates are globally blocked for all rooms.")

        # Ensure number of occupants does not exceed room capacity
        # if occupants > room.max_occupants:
            # raise ValidationError(f"Room's capacity is {room.max_occupants}. You cannot exceed this number.")

        return cleaned_data
