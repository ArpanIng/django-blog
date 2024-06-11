from django.urls import path

from . import views


app_name = "accounts"
urlpatterns = [
    path("me/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("comments/", views.UserCommentsListView.as_view(), name="comments"),
    path("likes/", views.UserPostLikesListView.as_view(), name="likes"),
]

# auth urls
urlpatterns += [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("signup/", views.CustomSignupView.as_view(), name="signup"),
    path(
        "password-change/",
        views.CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password-change/done/",
        views.CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password-reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
