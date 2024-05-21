from django.urls import path

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("search/", views.SearchView.as_view(), name="search"),
    path(
        "@<str:username>/<slug:post_slug>/",
        views.PostView.as_view(),
        name="post_detail",
    ),
    path("<slug:post_slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path(
        "<slug:post_slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"
    ),
]

urlpatterns += [
    path(
        "<slug:post_slug>/comment/<int:pk>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment_update",
    ),
    path(
        "<slug:post_slug>/comment/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]

urlpatterns += [
    path("<int:pk>/like/", views.PostLikeView.as_view(), name="post_like"),
]
