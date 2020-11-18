from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass
    #watch_list - this should represent a foreign key to the auction_listing model, such that there is a ManytoMany relationship between these
    #two models


class auction_list(models.Model):   
    auction_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "owner") 
    title = models.CharField(max_length = 64)
    description = models.CharField(max_length = 1200)
    starting_bid = models.IntegerField(validators=[MinValueValidator(1)])
    link = models.URLField(max_length = 200)  
    auction_category = models.CharField(max_length = 64)
    # - I think it will be helpful if I am able to provide pre-populated categories to the client at the time 
    #of creating the auction listing. I could also create a list of categories used by all clients and then use that as the starting point of the 
    #dropdown list of options that the user has 
    highest_bid = models.IntegerField(validators=[MinValueValidator(1)]) 
    status = models.BooleanField(default = False) 
    auction_winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "winner")
    watchlist_users = models.ManyToManyField(User, blank=True, related_name = "watchlistusers") 

    def __str__(self):
        return f"{self.id}, {self.auction_owner}, {self.title}, {self.description}, {self.starting_bid}, {self.link}, {self.auction_category}, {self.highest_bid}, {self.status}, {self.auction_winner}"


class bid(models.Model):
    bid_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "bidowner") #- this should be represented as a foreign key to the User model
    listing = models.ForeignKey(auction_list, on_delete=models.CASCADE, related_name = "bidlisting") #this should be represented as a foreign key to the auction_listing model 
    bid_amount = models.IntegerField() #this should represent the bid amount




class comment():
    pass 
    #comment_owner = models.Charfield - Should be represented as a foreign key to the user models
    #title = models.Charfield 
    #description = models.Charfield - this is going to represent the actual comment made by the user
    #associated_listing - Should be represented as a foreign key to the auction_listing models  



