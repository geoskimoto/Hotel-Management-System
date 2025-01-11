from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ImageField, FileInput, TextInput, Select
from userauths.models import Profile, User, MemberApplication
from .validators import validate_email


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': '', 'id': "", 'placeholder':'Full Name'}), max_length=100, required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': '', 'id': "", 'placeholder':'Username'}), max_length=100, required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': '' , 'id': "", 'placeholder':'Email Address'}), validators=[validate_email], required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "", 'placeholder':'Password'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "", 'placeholder':'Confirm Password'}), required=True)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'with-border'
            # visible.field.widget.attrs['placeholder'] = visible.field.label


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = [
            'image',
            'full_name', 
            'phone',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'gender',
            'date_of_birth',
            'emergency_contact',
            'emergency_contact_phone',
            'is_primary_member',
            'website_url',
            'joining_comments',
            'identity_type',
            'identity_image',

        ]
        widgets = {
            'image': FileInput(attrs={'onchange': 'loadFile(event)', 'class':'upload'}),
        }
        
class MemberApplicationForm(forms.ModelForm):
    class Meta:
        model = MemberApplication
        fields = '__all__'  # Include all fields from the model

        # Customizing widgets for specific fields
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'joining_comments': forms.Textarea(attrs={'class': 'ckeditor'}),
        }

    # Additional validation for phone_number (optional)
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Add custom validation logic here (e.g., length, format)
            # For example, checking the length:
            if len(phone_number) < 10 or len(phone_number) > 15:
                raise forms.ValidationError('Enter a valid phone number.')
        return phone_number