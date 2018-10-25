from django.shortcuts import render, HttpResponse, redirect
from .models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
import bcrypt
import re
import requests
import json
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

def index(request):
    return render(request, "snowmies/index.html")

def selectresort(request):
    if 'user_id' not in request.session:
        return redirect("/")
    context = {
        "user":User.objects.get(id=request.session['user_id'])
    }
    return render(request, "snowmies/resort.html", context)

def processresort(request):
    if 'user_id' not in request.session:
        return redirect("/")
    
    if request.method == "POST":
        request.session['resort'] = request.POST['resort']
    return redirect("/dashboard")

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect("/")

    rides = Ride.objects.all()
    for ride in rides:
        if datetime.utcnow() - timedelta(minutes=30) > ride.time.replace(tzinfo=None):
            print("!")
            # print(str(datetime.utcnow() + timedelta(minutes=30)))
            # print(str(ride.time.replace(tzinfo=None)))
            print("deleted ride")
            ride.delete()
    
    if request.session['resort'] == "Steven's Pass":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/47.7459,-121.0891")
    elif request.session['resort'] == "Crystal Mountain":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/47.0444,-121.94032")
    elif request.session['resort'] == "Mission Ridge":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/47.3348,-120.5771")
    elif request.session['resort'] == "Mount Bachelor":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/43.98287,-121.58095")
    elif request.session['resort'] == "Mount Hood Meadows":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/45.34357,-121.67227")
    elif request.session['resort'] == "The Summit at Snoqualmie":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/47.3923,-121.4543")
    elif request.session['resort'] == "Timberline Ski Resort":
        response = requests.get("https://api.darksky.net/forecast/0bf5a91e409e1a46e37e6766f0419d45/45.3311,-121.7110")
    # print(response.status_code)
    data = response.json()
    # data1 = data["hourly"]["data"][0]["temperature"]
    data1 = data["currently"]["temperature"]
    data2 = round(data["currently"]["precipProbability"]*100)
    data3 = data["currently"]["icon"]
    data4 = data["currently"]["summary"]
    # print(data1)
    # print(data2)
    print(data["currently"])
    # print(response.content)

    context = {
        "all_rides":Ride.objects.filter(resort=request.session['resort']).order_by("time"),
        "resort":request.session['resort'],
        "userid":request.session['user_id'],
        "forecast":data["daily"]["summary"],
        "temp":data1,
        "precip":data2,
        "icon":data3,
        "sum":data4,
    }
    return render(request, "snowmies/dashboard.html", context)

def addRide(request):
    if 'user_id' not in request.session:
        return redirect("/")
    context = {
        "resort":request.session['resort']
    }

    if request.method == "POST":
        return render(request, "snowmies/addride.html", context)

    return render(request, "snowmies/addride.html", context)

def processadd(request):
    if request.method == "POST":
        # print(str(datetime.now()))
        # print(request.POST["time"])

        if request.POST["time"] < str(datetime.now()):
            messages.warning(request, "Cannot add ride before today's date")
            return redirect("/addRide")
        if request.POST["time"] > str(datetime.now() + timedelta(days=90)):
            messages.warning(request, "You may only schedule rides at most 3 months ahead of time")
            return redirect("/addRide")
        if int(request.POST['min_age']) < 0 or int(request.POST['max_age']) < 0:
            messages.warning(request, "People cannot be less than 0 years old")
            return redirect("/addRide")
        if int(request.POST['min_age']) > int(request.POST['max_age']):
            messages.warning(request, "Minimum age must be less than the maximum age")
            return redirect("/addRide")

        ride = Ride()
        ride.resort = request.session['resort']
        ride.time = request.POST['time']
        ride.location = request.POST['location']
        ride.ride_with = request.POST['riders']
        ride.experience_lvl = request.POST['experience']
        ride.min_age = request.POST['min_age']
        ride.max_age = request.POST['max_age']
        ride.ride_type = request.POST['ride_type']
        ride.more = request.POST['more']
        ride.user = User.objects.get(id=request.session['user_id'])
        ride.save()
        return redirect("/dashboard") 
    return redirect("/addRide") 

def process(request):
    if request.method == "POST":
        user = User()
        if (len(request.POST["first_name"]) < 2):
            messages.warning(request, "First name must be at least 2 characters")
            return redirect("/")
        else:
            user.first_name = request.POST["first_name"]

        if (len(request.POST["last_name"])< 2):
            messages.warning(request,"Last name must be at least 2 characters")
            return redirect("/")
        else:
            user.last_name = request.POST["last_name"]
        
        if (len(request.POST["email"]) < 0) or not EMAIL_REGEX.match(request.POST["email"]):
            messages.warning(request,"Please enter a valid email")
            return redirect("/")
        else:
            user.email = request.POST["email"]

        if (len(request.POST["password"]) < 8):
            messages.warning(request,"Please enter a password with no fewer than 8 characters in length")
            return redirect("/")
        else:
            user.password = bcrypt.hashpw((request.POST["password"]).encode(), bcrypt.gensalt())

        if bcrypt.checkpw((request.POST["cpassword"]).encode(), user.password):
            user.save()
            request.session['user_id'] = user.id
        else:
            messages.warning(request,"password did not match")
            return redirect("/")        

    return redirect("/selectresort")

def edit(request, id):
    if 'user_id' not in request.session:
        return redirect("/")
    context = {
        "selectedride":Ride.objects.get(id=id),
        "resort":request.session['resort']
    }
    print(Ride.objects.get(id=id).time)
    return render(request, "snowmies/edit.html", context)

def processedit(request, id):
    if 'user_id' not in request.session:
        return redirect("/")
    if request.method == "POST":
        if request.POST["time"] < str(datetime.now()):
            messages.warning(request, "Cannot add ride before today's date")
            return redirect("/addRide")
        if request.POST["time"] > str(datetime.now() + timedelta(days=90)):
            messages.warning(request, "You may only schedule rides at most 3 months ahead of time")
            return redirect("/addRide")
        if int(request.POST['min_age']) < 0 or int(request.POST['max_age']) < 0:
            messages.warning(request, "People cannot be less than 0 years old")
            return redirect("/addRide")
        if int(request.POST['min_age']) > int(request.POST['max_age']):
            messages.warning(request, "Minimum age must be less than the maximum age")
            return redirect("/addRide")
        ride = Ride.objects.get(id=id)
        ride.resort = request.session['resort']
        ride.time = request.POST['time']
        ride.location = request.POST['location']
        ride.ride_with = request.POST['riders']
        ride.experience_lvl = request.POST['experience']
        ride.min_age = request.POST['min_age']
        ride.max_age = request.POST['max_age']
        ride.ride_type = request.POST['ride_type']
        ride.more = request.POST['more']
        ride.user = User.objects.get(id=request.session['user_id'])
        ride.save()
    return redirect("/dashboard")


def login(request):
    if request.method == "POST":
        if (len(request.POST["email"])) < 0 or not EMAIL_REGEX.match(request.POST["email"]):
            messages.warning(request,"email is too short or not formatted correctly")
            return redirect("/")
        try:
            user = User.objects.get(email=request.POST["email"])
        except ObjectDoesNotExist:
            messages.warning(request, "email doesnt match any accounts")
            return redirect("/")
        if (len(request.POST["password"])) < 8:
            messages.warning(request,"password isnt at least 8 characters")
            return redirect("/")
        
        if bcrypt.checkpw(request.POST["password"].encode(), user.password.encode()):
            request.session['user_id'] = user.id
            return redirect("/selectresort")
        else:
            messages.warning(request,"Wrong password")
            return redirect("/")

        return redirect("/")

def logout(request):
    del request.session['user_id']
    return redirect("/")

def remove(request, id):
    if 'user_id' not in request.session:
        return redirect("/")

    ride = Ride.objects.get(id=id)
    ride.delete()
    return redirect("/dashboard")

def destroy_data(request):
    b = User.objects.all()
    b.delete()
    a = Ride.objects.all()
    a.delete()
    return redirect("/")