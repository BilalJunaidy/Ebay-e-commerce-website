from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/bid/", views.Bid, name="bid"),
    path("listing/<int:listing_id>/close", views.close, name="close"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.specific_category, name="specific_category"),
    path("comments/<int:listing_id>", views.comments, name="comments"),
]
