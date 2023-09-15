from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("new/", views.PostCreateView.as_view(), name="post-create"),
    path("search/", views.SearchView.as_view(), name="search"),
    path(
        "@<str:username>/<slug:post_slug>/",
        views.PostDetailView.as_view(),
        name="post-detail",
    ),
    path("<slug:post_slug>/edit/", views.PostUpdateView.as_view(), name="post-update"),
    path(
        "<slug:post_slug>/delete/", views.PostDeleteView.as_view(), name="post-delete"
    ),
]

urlpatterns += [
    path(
        "<slug:post_slug>/comment/<int:pk>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "<slug:post_slug>/comment/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]

urlpatterns += [
    path("<slug:post_slug>/like/", views.LikeAddView.as_view(), name="like"),
    path("<slug:post_slug>/dislike/", views.DislikeAddView.as_view(), name="dislike"),
]
