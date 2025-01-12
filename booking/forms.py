# from django import forms
# from datetime import date
#
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