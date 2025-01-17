from django.contrib import admin
from .models import Room2, Booking2, BlockedDate

class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'check_in', 'check_out', 'user', 'occupants')
    search_fields = ('room__name', 'user', 'check_in', 'check_out', 'occupants')


class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('room', 'start_date', 'end_date', 'reason')
    search_fields = ('room__name', 'reason', 'start_date', 'end_date')


admin.site.register(Room2)
admin.site.register(Booking2, BookingAdmin)
admin.site.register(BlockedDate, BlockedDateAdmin)

