from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm

from .models import User, auction_list, bid, comment, Comment_Form

@login_required(login_url='login')
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

@login_required(login_url='login')
def create_listing(request):

    class auction_list_Form(ModelForm):
        class Meta:
            #link = forms.CharField(blank=True)

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

@login_required(login_url='login')
def listing(request, listing_id):

    class Bid_Form(ModelForm):
        class Meta:
            model = bid
            exclude = ['bid_owner','listing']
    modelform = Bid_Form()


    try: 
        listing = auction_list.objects.get(pk=listing_id)
    except:
        return HttpResponse("NO such listing exists")

    userqueryset = User.objects.filter(watchlistusers = listing)
    current_user_id = request.user.id
    min_bid_price = listing.highest_bid

    commentform = Comment_Form()

    current_comments = comment.objects.filter(listing = auction_list.objects.get(pk = listing_id))


    if not listing.auction_owner.id == current_user_id:
        owner = False 
    else:
        owner = True

    if current_user_id in userqueryset.values_list('id', flat=True):
        In_watchlist = True
    else:
        In_watchlist = False
    
    if listing.status == False:
        available = True
    else:
        available = False

    if not available and listing.auction_winner.id == current_user_id:
        win = True
    else:
        win = False
        

    ##watchlist = auction_list.objects.get(watchlist_user = User.objects.get(id=request.user.id))

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "In_watchlist": In_watchlist,
        "min_bid_price": min_bid_price,
        "owner": owner,
        "form": modelform,
        "available":available,
        "win": win, 
        "commentform": commentform,
        "current_comments": current_comments
        })

@login_required(login_url='login')
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

@login_required(login_url='login')        
def Bid(request, listing_id):

    class Bid_Form(ModelForm):
        class Meta:
            model = bid
            exclude = ['bid_owner','listing']

    if request.method == "POST":

        listing_object = auction_list.objects.get(pk=listing_id)
        min_bid_price = listing_object.highest_bid
        current_user_object = User.objects.get(pk=request.user.id)


        form = Bid_Form(request.POST)
        if form.is_valid():
            ##form.clean()
            if int(form.cleaned_data["bid_amount"]) < min_bid_price:
                return HttpResponse(f"Please enter a bid amount that is greater than the {min_bid_price}")
            
            else:
                listing_object.highest_bid = form.cleaned_data["bid_amount"]
                listing_object.save()

                submitted_bid = form.save(commit = False)
                submitted_bid.bid_owner = current_user_object
                submitted_bid.listing = listing_object
                form.save()
                return HttpResponseRedirect(reverse('index'))
            
        else:
            return HttpResponse(f"Your bid submission had an error. Please see error message below: \n\n{form.errors}")
    
    else:
        return HttpResponseRedirect(reverse("index"))
      
        #listing = auction_list.objects.filter(pk=listing_id).values('highest_bid')[0]['highest_bid']
        #listing = auction_list.objects.filter(pk=listing_id).first()['highest_bid']
        #min_bid_price = auction_list.objects.get(pk=listing_id).auction_owner.id  
        #return HttpResponse(f"bhains ---- {min_bid_price}")


@login_required(login_url='login')        
def close(request, listing_id):
    if request.method == 'POST':
        
        listing_object = auction_list.objects.get(pk = listing_id)
        if request.POST.get('option') == "close":
            listing_object.status = True
            listing_object.save()
            highest_bid_objects = bid.objects.filter(listing = listing_object)

            if not len(highest_bid_objects) == 0:
                highest_bid_object = highest_bid_objects.order_by('-bid_amount').first()
                listing_object.auction_winner = User.objects.get(pk = highest_bid_object.bid_owner.id)
                listing_object.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponse("oh bhains")


@login_required(login_url='login')
def categories(request):
    category_queryset = auction_list.objects.values_list('auction_category', flat=True).distinct()

    return render(request, "auctions/categories.html", {
        "categories": category_queryset})

@login_required(login_url='login')
def specific_category(request, category):
    
    specific_category_queryset = auction_list.objects.filter(auction_category = category)

    return render(request, "auctions/specific_category_query.html", {
        "listing": specific_category_queryset, 
        "category": category
    })
        
    return HttpResponse(f"welcome to {category}")

@login_required(login_url='login')
def comments(request, listing_id):
    if request.method == "POST":
        form = Comment_Form(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.owner = User.objects.get(pk = request.user.id)
            comment.listing = auction_list.objects.get(pk = listing_id)
            comment.save()

        return HttpResponseRedirect(reverse(index))


        
    else:
        return HttpResponseRedirect(reverse(index))









