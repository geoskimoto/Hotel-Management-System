from django.urls import path
from booking2 import views

app_name = "booking2"

urlpatterns = [
    # path('', views.home, name='home'),
    path('book/', views.book_room, name='book_room'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]