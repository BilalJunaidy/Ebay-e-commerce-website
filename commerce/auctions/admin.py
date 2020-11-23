from django.contrib import admin
from .models import User, auction_list, bid, comment


# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "auction_owner", "title", "description", "starting_bid", "link", "auction_category", "highest_bid", "status", "auction_winner")
admin.site.register(User)
admin.site.register(auction_list, AuctionAdmin)
admin.site.register(bid)
admin.site.register(comment)
