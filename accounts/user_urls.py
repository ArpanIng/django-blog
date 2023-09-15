from django.urls import path

from . import views


app_name = "users"
urlpatterns = [
    path("@<str:username>/follow/", views.AddFollowView.as_view(), name="follow"),
    path("@<str:username>/", views.ProfileView.as_view(), name="profile"),
    # path(
    #     "@<str:username>/followers/", views.FollowerListView.as_view(), name="followers"
    # ),
]
