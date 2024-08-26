from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Amenities,Hotel,HotelBooking
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# Create your views here.
def check_booking(start_date  , end_date ,uid , room_count):
    qs = HotelBooking.objects.filter(
        start_date__lte=start_date,
        end_date__gte=end_date,
        hotel__uid = uid
        )
    
    if len(qs) >= room_count:
        return False
    
    return True

@login_required(login_url='login')
def home(request):
    amenities_objs=Amenities.objects.all()
    hotels_objs=Hotel.objects.all()
    #work on sorted function
    sort_by=request.GET.get("sort_by")
    search=request.GET.get("search") 
    amni=request.GET.getlist("amenities")
    
    if sort_by:
        if sort_by=='ASC':
            hotels_objs=hotels_objs.order_by('hotel_price')
        elif sort_by=='DSC':
            hotels_objs=hotels_objs.order_by('-hotel_price')
    if search:
        hotels_objs=hotels_objs.filter(Q(hotel_name__icontains=search)|
                                       Q(description__icontains=search)|
                                       Q(amenities__amenities__icontains=search))
    
    if len(amni):
         hotels_objs=hotels_objs.filter(amenities__amenities__in=amni).distinct()

    context={"amenities_objs":amenities_objs,"hotels_objs":hotels_objs,"sort_by":sort_by}
    return render(request,'home.html',context)
@login_required(login_url='login')
def hotel_detail(request,uid):
      hotel_obj = Hotel.objects.get(uid = uid) 
      if request.method == 'POST':
        checkin = request.POST.get('checkin')
        checkout= request.POST.get('checkout')
        hotel = Hotel.objects.get(uid = uid)
        if not check_booking(checkin ,checkout  , uid , hotel.room_count):
            messages.warning(request, 'Hotel is already booked in these dates ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        HotelBooking.objects.create(hotel=hotel , user = request.user , start_date=checkin
        , end_date = checkout , booking_type  = 'Pre Paid')
        
        messages.success(request, 'Your booking has been saved')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

      return render(request , 'hotel_details.html',{'hotels_obj':hotel_obj} )

def login_page(request):
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user_obj=User.objects.filter(username=username)
        if not user_obj.exists():
            messages.warning(request,"account not found")#make a message.html that will automatic  catchj
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))#redirect on same page
        user_obj=authenticate(username=username,password=password)
        if not user_obj:
            messages.warning(request,"invalid")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))#redirect on same page
        login(request , user_obj)
        return redirect('/')
        
    return render(request,'login.html')
def register_page(request):
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user_obj=User.objects.filter(username=username)
        if user_obj.exists():
            messages.warning(request,"username is already taken"
            )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))#redirect on same page
        user=User.objects.create(username=username)
        user.set_password(password)
        user.save()
        return redirect('/')

    return render(request,'register.html')