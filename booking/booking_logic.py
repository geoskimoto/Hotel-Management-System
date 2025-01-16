from datetime import datetime
from hotel.models import Hotel, RoomType

def check_room_availability_data(id, checkin, checkout, room_type_slug):
    hotel = Hotel.objects.get(status="Live", id=id)
    room_type = RoomType.objects.get(hotel=hotel, slug=room_type_slug)

    return hotel, room_type

def calculate_room_selection_price(room_selection):
    total = 0
    total_days = 0
    room_count = 0
    adult = 0 
    children = 0 
    checkin = ""
    checkout = ""
    hotel = None

    for h_id, item in room_selection.items():
        id = int(item['hotel_id'])
        checkin = item["checkin"]
        checkout = item["checkout"]
        adult += int(item["adult"])
        children += int(item["children"])
        room_type_ = item["room_type"]

        hotel = Hotel.objects.get(id=id)
        room_type = RoomType.objects.get(id=room_type_)

        date_format = "%Y-%m-%d"
        checkin_date = datetime.strptime(checkin, date_format)
        checout_date = datetime.strptime(checkout, date_format)
        time_difference = checout_date - checkin_date
        total_days = time_difference.days

        room_count += 1
        days = total_days
        price = room_type.price
        room_price = price * room_count
        total = room_price * days

    return total, total_days, adult, children, hotel
