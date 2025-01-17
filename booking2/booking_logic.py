from datetime import timedelta
from django.http import JsonResponse
from datetime import timedelta


def is_room_available(room_id, check_in, check_out):
    if check_in >= check_out:
        return False

    # Check for overlapping bookings
    bookings = Booking.objects.filter(room_id=room_id)
    for booking in bookings:
        if (check_in < booking.check_out and check_out > booking.check_in):
            return False

    # Check for overlapping blocked dates
    blocked_dates = BlockedDate.objects.filter(room_id=room_id)
    for blocked_date in blocked_dates:
        if (check_in < blocked_date.end_date and check_out > blocked_date.start_date):
            return False  # Overlapping blocked date found

    return True  # No overlapping booking or blocked date found


def check_availability(request):
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    check_in = timezone.datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out = timezone.datetime.strptime(check_out, "%Y-%m-%d").date()

    available = is_room_available(room_id, check_in, check_out)

    return JsonResponse({'available': available})



