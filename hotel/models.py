from django.conf import settings
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.template.defaultfilters import escape
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_attachment_file_size
from django.core.exceptions import ValidationError
from userauths.models import User
import shortuuid
from datetime import timedelta
from taggit.managers import TaggableManager


# **NOTE** If you create a new model, make sure to register it in admin.py so it shows up in the admin dashboard after makemigrations and migrate.


ICON_TPYE = (
    ('Bootstap Icons', 'Bootstap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
)

ROOM_TYPES = (
    ('Bunk', 'Bunk'),
    ('Private Room', 'Private Room'),

)


FOOD_SERVICES_TYPES = (
    ('Breakfast', 'Breakfast'),
    ('Lunch', 'Lunch'),
    ('Dinner', 'Dinner'),
    ('Special Event Meal', 'Special Event Meal')
)

HOTEL_STATUS = (
    # ("Draft", "Draft"),
    ("Disabled", "Disabled"),
    # ("Rejected", "Rejected"),
    # ("In Review", "In Review"),
    ("Live", "Live"),
)

GENDER = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Non-binary", "Non-binary"),
    ("Prefer not to say", "Prefer not to say")
)


DISCOUNT_TYPE = (
    ("Percentage", "Percentage"),
    ("Flat Rate", "Flat Rate"),
)

PAYMENT_STATUS = (
    ("paid", "Paid"),
    # ("pending", "Pending"),
    ("processing", "Processing"),
    ("cancelled", "Cancelled"),
    ("initiated", 'Initiated'),
    ("failed", 'failed'),
    # ("refunding", 'refunding'),
    ("refunded", 'refunded'),
    # ("unpaid", 'unpaid'),
    # ("expired", 'expired'),
)



NOTIFICATION_TYPE = (
    ("Booking Confirmed", "Booking Confirmed"),
    ("Booking Cancelled", "Booking Cancelled"),
)


RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)

class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    image = models.FileField(upload_to="hotel_gallery")
    address = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    status = models.CharField(choices=HOTEL_STATUS, max_length=10, default="published", null=True, blank=True)

    tags = TaggableManager(blank=True)
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
            
        super(Hotel, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))

    def hotel_gallery(self):
        return HotelGallery.objects.filter(hotel=self)
    
    def hotel_features(self):
        return HotelFeatures.objects.filter(hotel=self)

    def hotel_faqs(self):
        return HotelFAQs.objects.filter(hotel=self)

    def hotel_room_types(self):
        return RoomType.objects.filter(hotel=self)
    
    def average_rating(self):
        average_rating = Review.objects.filter(hotel=self, active=True).aggregate(avg_rating=models.Avg("rating"))
        return average_rating['avg_rating']
    
    def rating_count(self):
        rating_count = Review.objects.filter(hotel=self, active=True).count()
        return rating_count
    
class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    image = models.FileField(upload_to="hotel_gallery")
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")

    def __str__(self):
        return str(self.hotel)

    class Meta:
        verbose_name_plural = "Hotel Gallery"
    

class HotelFeatures(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TPYE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")

    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Hotel Features"
    
class HotelFAQs(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")

    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Hotel FAQs"

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    member_price = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    child_price = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    guest_price = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    number_of_beds = models.PositiveIntegerField(default=1)
    room_capacity = models.PositiveIntegerField(default=1)
    rtid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.hotel.name}"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.type) + "-" + str(uniqueid.lower())
            
        super(RoomType, self).save(*args, **kwargs) 
    

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    rid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.type} -  Room {self.room_number}"

    def member_price(self):
        return self.room_type.member_price
    def child_price(self):
        return self.room_type.member_price
    def guest_price(self):
        return self.room_type.member_price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated")

    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=1000, null=True, blank=True)
    
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    # room = models.ManyToManyField(Room)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', null=True)

    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_days = models.PositiveIntegerField(default=0)
    num_members = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    num_guests = models.PositiveIntegerField(default=0)
    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    checked_in_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    checked_out_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    coupons = models.ManyToManyField("hotel.Coupon", blank=True)
    stripe_payment_intent = models.CharField(max_length=200,null=True, blank=True)
    success_id = ShortUUIDField(length=300, max_length=505, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")

    def __str__(self):
        return f"{self.booking_id}"
    
    def rooms(self):
        return self.room.all().count()
    
    def validation_checks(self):
        """
        Custom validations for booking: ensure room is available, dates are valid, occupancy is within limits.
        """
        # Booking must not overlap
        if Booking.objects.filter(room=self.room, check_in_date__lt=self.check_out_date, check_out_date__gt=self.check_in_date).exists():
            raise ValidationError(f"The room {self.room.name} is already booked for these dates.")

        # Check against blocked dates for the room
        if BlockedDate.objects.filter(room=self.room, start_date__lt=self.check_out_date, end_date__gt=self.check_in_date).exists():
            raise ValidationError(f"The room {self.room.name} is blocked for these dates.")
        
        if BlockedDate.objects.filter(room=None, start_date__lt=self.check_out_date, end_date__gt=self.check_in_date).exists():
            raise ValidationError("These dates are globally blocked for all rooms.")

        # Ensure check-out is after check-in
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Check-out date must be after check-in date.")
        
        # Ensure booking dates are not in the past
        if self.check_in_date < settings.MIN_BOOKING_DATE:
            raise ValidationError("Booking cannot be made for past dates.")
        
        # Ensure booking stays are within the allowed duration window
        booking_duration = self.check_out_date - self.check_in_date
        if booking_duration < timedelta(days=settings.MIN_STAY_DAYS):
            raise ValidationError(f"Stay must be at least {settings.MIN_STAY_DAYS} days.")
        
        if booking_duration > timedelta(days=settings.MAX_STAY_DAYS):
            raise ValidationError(f"Stay cannot exceed {settings.MAX_STAY_DAYS} days.")
        
        # Ensure the number of occupants is within the room's capacity
        if self.occupants > self.room.max_occupants:
            raise ValidationError(f"Room capacity exceeded. Maximum occupants: {self.room.max_occupants}.")
        
    def save(self, *args, **kwargs):
        
        # Run custom validation checks
        self.validation_checks()
        
        # Calculate total days before saving
        self.total_days = (self.check_out_date - self.check_in_date).days
        
        # Calculate total price:
        member_price = self.room_type.member_price
        child_price = self.room_type.child_price
        guest_price = self.room_type.guest_price
        
        total_member_price = (member_price * self.num_members * self.total_days)
        total_child_price = (child_price * self.num_members * self.total_days)
        total_guest_price = (guest_price * self.num_members * self.total_days)
        
        self.total = total_member_price + total_child_price + total_guest_price
        
        super(Booking, self).save(*args, **kwargs)

        print(f"Booking for {self.user} from {self.check_in_date} to {self.check_out_date} was successfully instantiated and entered into the database.")

class BlockedDate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='blocked_dates')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200)

    def __str__(self):
        return f"Blocked from {self.start_date} to {self.end_date} for {self.reason}"
        
class ActivityLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    guest_out = models.DateTimeField()
    guest_in = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.booking)
    
class StaffOnDuty(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    staff_id = models.CharField(null=True, blank=True, max_length=100)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.staff_id)
    

class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
    redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    make_public = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_to = models.DateField()
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz1234567890")

    
    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']


class CouponUsers(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.coupon.code)
    
    class Meta:
        ordering =['-id']


class FoodServices(models.Model):
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    service_type = models.CharField(max_length=20, choices=FOOD_SERVICES_TYPES)
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    def str(self):
        return str(self.booking) + " " + str(self.room) + " " + str(self.service_type)


class MemberNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="member_news")
    date= models.DateField(auto_now_add=True)
    subject = CKEditor5Field(config_name='extends', null=True, blank=True)
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    is_news = models.BooleanField(default=True)
    is_event = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, validators=[validate_attachment_file_size])

class PublicNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="public_news")
    date= models.DateField(auto_now_add=True)
    subject = CKEditor5Field(config_name='extends', null=True, blank=True)
    description = CKEditor5Field(config_name='extends', null=True, blank=True)
    is_news = models.BooleanField(default=True)
    is_event = models.BooleanField(default=False) 
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, validators=[validate_attachment_file_size])    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="notifications")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=100, default="new_order", choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    nid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
    date= models.DateField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['-date']



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        return f"{self.user.username} - {self.rating}"
        