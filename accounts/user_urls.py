from django.urls import path

from . import views


app_name = "users"
urlpatterns = [
    path("@<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("@<str:username>/about/", views.UserAboutView.as_view(), name="user_about"),
    path(
        "@<str:username>/following/",
        views.FollowingListView.as_view(),
        name="following",
    ),
    path(
        "@<str:username>/followers/",
        views.FollowersListView.as_view(),
        name="followers",
    ),
    path(
        "follow-toggle/<int:pk>/",
        views.FollowToggleView.as_view(),
        name="follow-toggle",
    ),
]
