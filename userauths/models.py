from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.db.models.signals import post_save
from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.dispatch import receiver


from PIL import Image
from shortuuid.django_fields import ShortUUIDField
import os 


# **NOTE** If you create a new model, make sure to register it in admin.py so it shows up in the admin dashboard after makemigrations and migrate.

IDENTITY_TYPE = (
    ("drivers_licence", "Drivers Licence"),
    ("international_passport", "International Passport")
)

GENDER = (
    ("female", "Female"),
    ("male", "Male"),
    ("non-binary", "Non-binary"),
    ("prefer_not_to_say", "Prefer not to say")
)

TITLE = (
    ("Mr", "Mr"),
    ("Mrs", "Mrs"),
    ("Miss", "Miss"),
)


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id,  filename)

class User(AbstractUser):
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True)

    otp = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username



class Profile(models.Model):
    pid = ShortUUIDField(length=7, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz123")
    image = models.ImageField(upload_to=user_directory_path, default="default.jpg", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)

    address = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    website_url = models.URLField(max_length=100, blank=True)
    joining_comments = models.TextField(max_length=2000, blank=True)
    emergency_contact = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=13, null=True, blank=True)
    is_primary_member = models.BooleanField(default=True)
    is_spouse_member = models.BooleanField(default=False)
    is_child_member = models.BooleanField(default=False)

    # family_member1 = models.CharField(max_length=100, null=True, blank=True)
    # family_member2 = models.CharField(max_length=100, null=True, blank=True)
    # family_member3 = models.CharField(max_length=100, null=True, blank=True)
    # family_member4 = models.CharField(max_length=100, null=True, blank=True)
    # family_member5 = models.CharField(max_length=100, null=True, blank=True)
    # family_member6 = models.CharField(max_length=100, null=True, blank=True)

    is_employee = models.BooleanField(default=False)
    is_committee_member = models.BooleanField(default=False)
    
    identity_type = models.CharField(choices=IDENTITY_TYPE, default="drivers_license", max_length=100, null=True, blank=True)
    identity_image = models.ImageField(upload_to=user_directory_path, default="id.jpg", null=True, blank=True)

    wallet = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)
    verified = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else:
            return f"{self.user.username}"
        
    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.username
            
        super(Profile, self).save(*args, **kwargs) 
    
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" />' % (self.image))

    
    
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

class MemberApplication(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    date_of_birth = models.DateField()
    occupation = models.CharField(max_length=50)
    skills = models.CharField(max_length=400, blank=True)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='USA')
    phone_number = models.CharField(max_length=30, blank=True) #make this with more appropriate constraints/formating.
    website_url = models.URLField(max_length=100, blank=True)
    joining_comments = CKEditor5Field(config_name='extends', null=True, blank=True)
 
class ApprovedEmail(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email   
    
@receiver(models.signals.pre_delete, sender=Profile)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if os.path.exists(image_path):
            os.remove(image_path)

