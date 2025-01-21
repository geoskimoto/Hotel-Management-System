from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from booking.forms import BookingForm


from hotel.models import Coupon, CouponUsers, Hotel, Room, Booking, PublicNews, MemberNews, FoodServices, HotelGallery, HotelFeatures, RoomType, Notification, Bookmark, Review

from datetime import datetime
from decimal import Decimal
import stripe
import json


def index(request):
    hotel = Hotel.objects.filter(status="Live")
    publicnews = PublicNews.objects.filter(is_news=True).order_by('-date')[:5]
    context = {
        "hotel":hotel,
        "PublicNews":publicnews
    }
    return render(request, "hotel/index.html", context)


# This is to go to the hotel detail page which is where the booking/checking availability
#  of a room actually takes place (i.e. when you hit "make a booking"
# in the admin dashboard it uses this view and template).
def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    print(f"I'm in hotel_detail() in booking.views.  Hotel has the following room types: {hotel.roomtype_set.all()}")  # Debugging line
    form = BookingForm()
    context = {
        "hotel":hotel,
        "form":form
        
    }
    return render(request, "hotel/hotel_detail.html",  context=context) # {'form': form}) #,


# After you hit "Check Availability" in the hotel_detail.html (view above) it takes you to room_type_detail.html
# where you see a collection of rooms that are available.
def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type = RoomType.objects.get(hotel=hotel, slug=rt_slug)
    rooms = Room.objects.filter(room_type=room_type, is_available=True)

    id = request.GET.get("hotel-id")
    check_in_date = request.GET.get("check_in_date")
    check_out_date = request.GET.get("check_out_date")
    num_members = request.GET.get("num_members")
    num_children = request.GET.get("num_children")
    num_guests = request.GET.get("num_guests")
    room_type_ = request.GET.get("room-type")

    # request.session['hotel'] = hotel
    # request.session['room_type'] = room_type
    request.session['room_type_'] = room_type_
    # request.session['rooms'] = rooms
    request.session['check_in_date'] = check_in_date
    request.session['check_out_date'] = check_out_date
    request.session['num_members'] = num_members
    request.session['num_children'] = num_children
    request.session['num_guests'] = num_guests
        

    if not all([check_in_date, check_out_date]):
        messages.warning(request, "Please enter your booking data to check availability.")
        return redirect("booking:booking_data", hotel.slug)
    
    context = {
        "hotel":hotel,
        "room_type":room_type,
        "rooms":rooms,
        "id":id,
        "check_in_date":check_in_date,
        "check_out_date":check_out_date,
        "num_members":num_members,
        "num_children":num_children,
        "room_type_":room_type_,
    }
    return render(request, "hotel/room_type_detail.html", context)


#This is the view to see items in the shopping cart.
def selected_rooms(request):
    # request.session.pop('selection_data_obj', None)

    total = 0
    room_count = 0
    total_days = 0
    members = 0 
    children = 0 
    guests = 0
    checkin = "0" 
    checkout = "" 
    children = 0 
    
    if 'selection_data_obj' in request.session:

        if request.method == "POST":
            for h_id, item in request.session['selection_data_obj'].items():
                print(f'item: {type(item)}')
                id = int(item['hotel_id'])
                print(id)
                hotel_id = int(item['hotel_id'])

                check_in_date = item["check_in_date"]
                check_out_date = item["check_out_date"]
                num_members = int(item["num_members"])
                num_children = int(item["num_children"])
                num_guests = int(item['num_guests'])
                room_type_ = item["room_type"]
                room_id = int(item["room_id"])
                
                user = request.user
                hotel = Hotel.objects.get(id=id)
                room = Room.objects.get(id=room_id)
                room_type = RoomType.objects.get(id=room_type_)

                

                
            date_format = "%Y-%m-%d"
            check_in_date = datetime.strptime(check_in_date, date_format)
            check_out_date = datetime.strptime(check_out_date, date_format)
            # time_difference = check_out_date - check_in_date
            # total_days = time_difference.days

            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")

            booking = Booking.objects.create(
                hotel=hotel,
                room_type=room_type,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                # total_days=total_days,
                num_members=num_members,
                num_children=num_children,
                num_guests=num_guests,
                full_name=full_name,
                email=email,
                phone=phone
            )
            if request.user.is_authenticated:
                booking.user = request.user
                booking.save()
            else:
                booking.user = None
                booking.save()


            # for h_id, item in request.session['selection_data_obj'].items():
            #     room_id = int(item["room_id"])
            #     room = Room.objects.get(id=room_id)
            #     booking.room.add(room)

            #     room_count += 1
            #     days = booking.total_days
            #     member_price = booking.room_type.member_price
            #     children_price = booking.room_type.child_price
            #     price = booking.room_type.member_price
                
            #     room_price = member_price * room_count
            #     total = room_price * days

                # print("room_price ==",room_price)
                # print("total ==",total)
            
            # booking.total += float(total)
            # booking.before_discount += float(total)
            # booking.save()

            messages.success(request, "Checkout Now!")
            return redirect("hotel:checkout", booking.booking_id)

        hotel = None

        for h_id, item in request.session['selection_data_obj'].items():
            
            
            id = int(item['hotel_id'])
            print(id)
            hotel_id = int(item['hotel_id'])

            check_in_date = item["check_in_date"]
            check_out_date = item["check_out_date"]
            num_members = int(item["num_members"])
            num_children = int(item["num_children"])
            num_guests = int(item['num_guests'])
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])
            
            user = request.user
            hotel = Hotel.objects.get(id=id)
            room = Room.objects.get(id=room_id)
            room_type = RoomType.objects.get(id=room_type_)
            
            room_type = RoomType.objects.get(id=room_type_)

            
            hotel = Hotel.objects.get(id=id)

        print("hotel ===", hotel)
        context = {
            "data":request.session['selection_data_obj'], 
            "total_selected_items": len(request.session['selection_data_obj']),
            "total":booking.total,
            "total_days":booking.total_days,
            "num_members":booking.num_members,
            "num_children":booking.num_children,   
            "check_in_date":check_in_date,   
            "check_out_date":check_out_date,   
            "hotel":hotel,   
        }

        return render(request, "hotel/selected_rooms.html", context)
    else:
        messages.warning(request, "You don't have any room selections yet!")
        return redirect("/")

def checkout(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    if booking.payment_status == "paid":
        messages.success(request, "This order has been paid for!")
        return redirect("/")
    else:
        booking.payment_status = "processing"
        booking.save()


    # Coupon
    now = timezone.now()
    if request.method == "POST":
        # Get code entered in the input field
        code = request.POST.get('code')
        print("code ======", code)
        try:
            coupon = Coupon.objects.get(code__iexact=code,valid_from__lte=now,valid_to__gte=now,active=True)
            if coupon in booking.coupons.all():
                messages.warning(request, "Coupon Already Activated")
                return redirect("hotel:checkout", booking.booking_id)
            else:
                CouponUsers.objects.create(
                    booking=booking,
                    coupon=coupon,
                    full_name=booking.full_name,
                    email=booking.email,
                    mobile=booking.phone,
                )

                if coupon.type == "Percentage":
                    discount = booking.total * coupon.discount / 100
                else:
                    discount = coupon.discount

                booking.coupons.add(coupon)
                booking.total -= discount
                booking.saved += discount
                booking.save()

                
                messages.success(request, "Coupon Found and Activated")
                return redirect("hotel:checkout", booking.booking_id)
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon Not Found")
            return redirect("hotel:checkout", booking.booking_id)
    
    context = {
        "booking":booking,  
        "stripe_publishable_key":settings.STRIPE_PUBLIC_KEY,
        "flutter_publick_key":settings.FLUTTERWAVE_PUBLIC,
        "website_address":settings.WEBSITE_ADDRESS,
    }
    return render(request, "hotel/checkout.html", context)


@csrf_exempt
def create_checkout_session(request, booking_id):
    request_data = json.loads(request.body)
    booking = get_object_or_404(Booking, booking_id=booking_id)

    stripe.api_key = settings.STRIPE_PRIVATE_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = booking.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': booking.full_name,
                    },
                    'unit_amount': int(booking.total * 100),
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('hotel:success', args=[booking.booking_id])) + "?session_id={CHECKOUT_SESSION_ID}&success_id="+booking.success_id+'&booking_total='+str(booking.total),
        cancel_url=request.build_absolute_uri(reverse('hotel:failed', args=[booking.booking_id]))+ "?session_id={CHECKOUT_SESSION_ID}",
    )

    booking.payment_status = "processing"
    booking.stripe_payment_intent = checkout_session['id']
    booking.save()

    print("checkout_session ==============", checkout_session)
    return JsonResponse({'sessionId': checkout_session.id})


def payment_success(request, booking_id):
    success_id = request.GET.get('success_id')
    booking_total = request.GET.get('booking_total')

    if success_id and booking_total: 
        success_id = success_id.rstrip('/')
        booking_total = booking_total.rstrip('/')
        
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        
        # Payment Verification
        if booking.total == Decimal(booking_total):
            if booking.payment_status == "processing": #processing #paid
                booking.payment_status = "paid"
                booking.save()

                noti = Notification.objects.create(booking=booking,type="Booking Confirmed",)
                if request.user.is_authenticated:
                    noti.user = request.user
                    noti.save()
                else:
                    noti = None
                    noti.save()

                # Delete the Room Sessions
                if 'selection_data_obj' in request.session:
                    del request.session['selection_data_obj']
                
                # Send Email To Customer
                merge_data = {
                    'booking': booking, 
                    'booking_rooms': booking.room.all(), 
                    'full_name': booking.full_name, 
                    'subject': f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}", 
                }
                subject = f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}"
                text_body = render_to_string("email/booking_completed.txt", merge_data)
                html_body = render_to_string("email/booking_completed.html", merge_data)
                
                msg = EmailMultiAlternatives(
                    subject=subject, 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.email], 
                    body=text_body
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                    
            elif booking.payment_status == "paid":
                messages.success(request, f'Your booking has been completed.')
                return redirect("/")
            else:
                messages.success(request, 'Opps... Internal Server Error; please try again later')
                return redirect("/")
                
        else:
            messages.error(request, "Error: Payment Issue Detected, This payment have been cancelled")
            booking.payment_status = "failed"
            booking.save()
            return redirect("/")
    else:
        messages.error(request, "Error: Payment Issue Detected, This payment have been cancelled")
        booking = Booking.objects.get(booking_id=booking_id, success_id=success_id)
        booking.payment_status = "failed"
        booking.save()
        return redirect("/")
    
    context = {
        "booking": booking, 
        'rooms':booking.room.all(), 
    }
    return render(request, "hotel/payment_success.html", context) 


def payment_failed(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    booking.payment_status = "failed"
    booking.save()
                
    context = {
        "booking": booking, 
    }
    return render(request, "hotel/payment_failed.html", context) 


def invoice(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)

    context = {
        "booking":booking,  
        "room":booking.room.all(),  
    }
    return render(request, "hotel/invoice.html", context)

@csrf_exempt
def update_room_status(request):
    today = timezone.now().date()

    booking = Booking.objects.filter(is_active=True, payment_status="paid")   
    for b in booking:
        if b.checked_in_tracker != True:
            if b.check_in_date > today:
                b.checked_in_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()
                

            else:
                b.checked_in_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()
        else:
            if b.check_out_date > today:
                b.checked_out_tracker = False
                b.save()

                for r in b.room.all():
                    r.is_available = False
                    r.save()

            else:
                b.checked_out_tracker = True
                b.save()

                for r in b.room.all():
                    r.is_available = True
                    r.save()
                    
    return HttpResponse(today)



def rates(request):
    return render(request, 'hotel/rates.html')

def membership_rates(request):
    return render(request, 'hotel/membership_rates.html')

def faq(request):
    return render(request, 'hotel/faq.html')

def news(request):
    return render(request, 'hotel/news.html')