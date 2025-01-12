from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist


from hotel.models import Hotel, Room, Booking, FoodServices, HotelGallery, HotelFeatures, RoomType

from datetime import datetime
from decimal import Decimal

def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        # adult = request.POST.get("adult")
        # children = request.POST.get("children")
        room_type = request.POST.get("room-type")

        hotel = Hotel.objects.get(status="Live", id=id)
        room_type = RoomType.objects.get(hotel=hotel, slug=room_type)

        print("id ====", id)
        print("room_type ====", room_type)
        print("checkin ====", checkin)
        print("checkout ====", checkout)
        # print("adult ====", adult)
        # print("children ====", children)

        # return redirect("hotel:room_type_detail", hotel.slug, room_type.slug)
        url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type.slug])
        # url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&adult={adult}&children={children}&room_type={room_type}"
        url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&room_type={room_type}"
        return HttpResponseRedirect(url_with_params)

    else:
        return redirect("hotel:index")

# def check_room_availability(request):
#     if request.method == 'POST':
#         form = AvailabilityForm(request.POST)
#         if form.is_valid():
#             # Process the valid form data here
#             # You can get the cleaned data using form.cleaned_data
#             return render(request, 'booking/availability_result.html', {'form': form})
#     else:
#         form = AvailabilityForm()
#
#     return render(request, 'booking/room_availability.html', {'form': form})

def booking_data(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    context = {
        "hotel":hotel,
    }
    return render(request, "booking/booking_data.html", context)




def add_to_selection(request):
    # Extract GET parameters
    room_selection = {}
    hotel_id = request.GET.get('hotel_id')
    hotel_name = request.GET.get('hotel_name')
    room_name = request.GET.get('room_name')
    room_price = request.GET.get('room_price')
    number_of_beds = request.GET.get('number_of_beds')
    room_number = request.GET.get('room_number')
    room_type = request.GET.get('room_type')
    room_id = request.GET.get('room_id')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    # adult = request.GET.get('adult')
    # children = request.GET.get('children')

    # Validate required fields
    if not all([hotel_id, hotel_name, room_name, room_price, number_of_beds, room_number, room_type, room_id, checkin,
                checkout]):
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    room_selection[str(request.GET['id'])] = {
        'hotel_id': hotel_id,
        'hotel_name': hotel_name,
        'room_name': room_name,
        'room_price': room_price,
        'number_of_beds': number_of_beds,
        'room_number': room_number,
        'room_type': room_type,
        'room_id': room_id,
        'checkin': checkin,
        'checkout': checkout,
        'adult': int(adult),  # Ensure 'adult' is an integer
        'children': int(children),  # Ensure 'children' is an integer
    }

    # Update the session if 'selection_data_obj' already exists in the session
    if 'selection_data_obj' in request.session:
        selection_data = request.session['selection_data_obj']

        if str(request.GET['id']) in selection_data:
            # Update existing selection data
            # selection_data[str(request.GET['id'])]['adult'] = int(adult)
            # selection_data[str(request.GET['id'])]['children'] = int(children)
            request.session['selection_data_obj'] = selection_data
        else:
            # Add new selection data
            selection_data.update(room_selection)
            request.session['selection_data_obj'] = selection_data
    else:
        # Save the room selection if it's the first time adding to the session
        request.session['selection_data_obj'] = room_selection

    # Prepare the response data
    data = {
        "data": request.session['selection_data_obj'],
        'total_selected_items': len(request.session['selection_data_obj'])
    }
    return JsonResponse(data)


def delete_session(request):
    request.session.pop('selection_data_obj', None)
    return redirect(request.META.get("HTTP_REFERER"))


def delete_selection(request):
    hotel_id = request.GET.get('id', None)
    if hotel_id is None:
        return JsonResponse({"error": "ID is missing from the request."}, status=400)
    if 'selection_data_obj' in request.session:
        if hotel_id in request.session['selection_data_obj']:
            selection_data = request.session['selection_data_obj']
            del request.session['selection_data_obj'][hotel_id]
            request.session['selection_data_obj'] = selection_data


    total = 0
    total_days = 0
    room_count = 0
    # adult = 0
    # children = 0
    checkin = "" 
    checkout = "" 
    hotel = None

    if 'selection_data_obj' in request.session:
        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            # adult += int(item["adult"])
            # children += int(item["children"])
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
        
    
    context = render_to_string(
        "hotel/async/selected_rooms.html",
        {
            "data":request.session['selection_data_obj'],
            "total_selected_items": len(request.session['selection_data_obj']),
            "total":total,
            "total_days":total_days,
            # "adult":adult,
            # "children":children,
            "checkin":checkin,
            "checkout":checkout,
            "hotel":hotel
        }
    )

    print("data ======", context)
    
    return JsonResponse({"data": context, 'total_selected_items': len(request.session['selection_data_obj'])})

