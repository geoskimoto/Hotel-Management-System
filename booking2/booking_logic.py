from datetime import timedelta
from django.http import JsonResponse
from datetime import timedelta
from models import Booking2, Room2, BlockedDate
from django.db.models.signals import post_save
from django.dispatch import receiver

 
    
    
def is_room_available(room_id, check_in, check_out):
    if check_in >= check_out:
        return False

    # Check for overlapping bookings
    bookings = Booking2.objects.filter(room_id=room_id)
    for booking in bookings:
        if (check_in < booking.check_out and check_out > booking.check_in):
            return False

    # Check for overlapping blocked dates
    blocked_dates = BlockedDate.objects.filter(room_id=room_id)
    for blocked_date in blocked_dates:
        if (check_in < blocked_date.end_date and check_out > blocked_date.start_date):
            return False  # Overlapping blocked date found

    return True  # No overlapping booking or blocked date found

from django.db import transaction



# This function is using db transactions to ensure atomic operations and ability to roll back transactions
# if any part were to fail, preventing partial updates that could lead to double booking.
# Additionally, using the .select_for_updates() function implements Pessimistic locking
def book_room(room_id, check_in, check_out):
    with transaction.atomic():
        room = Room2.objects.select_for_update().get(id=room_id)
        if not is_room_available(room_id, check_in, check_out):
            raise Exception("Room is not available")
        # Booking.objects.create(room=room_id, check_in=check_in, check_out=check_out)        
        Booking2.objects.create(room=room, check_in=check_in, check_out=check_out)


# If Pessimitic locking is too harsh and prevents admin from viewing bookings are things to fail, try using optimistic locking.
# Optimistic locking checks if the data has changed since it was last read, before committing the changes.
# This can be implemented by including a version or timestamp in the booking record.

# class Booking(models.Model):
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
#     check_in = models.DateField()
#     check_out = models.DateField()
#     version = models.IntegerField(default=0)

# def book_room(room_id, check_in, check_out):
#     with transaction.atomic():
#         room = Room.objects.select_for_update().get(id=room_id)
#         last_version = room.bookings.latest('version').version
#         if not is_room_available(room_id, check_in, check_out):
#             raise Exception("Room is not available")
#         # Increment version and create booking
#         Booking.objects.create(room=room, check_in=check_in, check_out=check_out, version=last_version + 1)


def check_availability(request):
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    check_in = timezone.datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out = timezone.datetime.strptime(check_out, "%Y-%m-%d").date()

    available = is_room_available(room_id, check_in, check_out)

    return JsonResponse({'available': available})


@receiver(post_save, sender=Booking)
def update_room_capacity(sender, instance, **kwargs):
    room = instance.room
    room.capacity -= instance.guests  # Decrease the capacity by the number of booked guests
    room.save()
   