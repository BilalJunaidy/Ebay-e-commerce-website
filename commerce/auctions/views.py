from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm

from .models import User, auction_list, bid_model


##@login_required
def index(request):
    active_listings = auction_list.objects.filter(status=False)
    return render(request, "auctions/index.html", {
        "listing": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):

    class auction_list_Form(ModelForm):
        class Meta:
            model = auction_list
            exclude = ['auction_owner', 'auction_winner', 'status', 'highest_bid', 'watchlist_users']

    if request.method == "POST":
        form = auction_list_Form(request.POST)

        if form.is_valid():
            form.clean()
             
            listing = form.save(commit = False)
            current_user = User.objects.get(id=request.user.id)
            listing.auction_owner = current_user
            listing.auction_winner = current_user
            listing.highest_bid = form.cleaned_data["starting_bid"]
            listing.save()
            
            return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
            
    modelform = auction_list_Form()
    return render(request, "auctions/create_listing.html", {
        "form": modelform
    })

def listing(request, listing_id):

    class Bid_Form(ModelForm):
        class Meta:
            model = bid_model
            exclude = ['bid_owner','listing']
    modelform = Bid_Form()


    try: 
        listing = auction_list.objects.get(pk=listing_id)
    except:
        return HttpResponse("NO such listing exists")

    userqueryset = User.objects.filter(watchlistusers = listing)
    current_user_id = request.user.id
    min_bid_price = listing.highest_bid

    if not listing.auction_owner.id == current_user_id:
        owner = False 
    else:
        owner = True

    if current_user_id in userqueryset.values_list('id', flat=True):
        In_watchlist = True
    else:
        In_watchlist = False
        

    ##watchlist = auction_list.objects.get(watchlist_user = User.objects.get(id=request.user.id))

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "In_watchlist": In_watchlist,
        "min_bid_price": min_bid_price,
        "owner": owner,
        "form": modelform
        })

def watchlist(request):
    current_user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        
        listing_id = request.POST["listing_id"]
        listing = auction_list.objects.get(pk = listing_id)

        if request.POST["update"] == "add":
            listing.watchlist_users.add(current_user)
        else:
            listing.watchlist_users.remove(current_user)
        
        return HttpResponseRedirect(reverse("index"))
    else:
        listing = auction_list.objects.filter(watchlist_users = current_user)
        return render(request, "auctions/watchlist.html", {
        "listing": listing
        })
        
def Bid(request, listing_id):

    class Bid_Form(ModelForm):
        class Meta:
            model = bid_model
            exclude = ['bid_owner','listing']

    if request.method == "POST":

        listing_object = auction_list.objects.get(pk=listing_id)
        min_bid_price = listing_object.highest_bid
        current_user_object = User.objects.get(pk=request.user.id)


        form = Bid_Form(request.POST)
        if form.is_valid():
            form.clean()
            if form.cleaned_data["bid_amount"] < min_bid_price:
                return HttpResponse(f"Please enter a bid amount that is greater than the {min_bid_price}")
            else:
                bid = form.save(commit = False)
                bid.bid_owner = current_user_object
                bid.listing = listing_object
                form.save()


        return HttpResponse("U have just made a POST request")
      
        #listing = auction_list.objects.filter(pk=listing_id).values('highest_bid')[0]['highest_bid']
        #listing = auction_list.objects.filter(pk=listing_id).first()['highest_bid']
        #min_bid_price = auction_list.objects.get(pk=listing_id).auction_owner.id  
        #return HttpResponse(f"bhains ---- {min_bid_price}")
    else:
        return HttpResponseRedirect(reverse('index'))
        


        
