from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from taggit.models import Tag

from .forms import CommentModelForm, PostModelForm
from .models import Comment, Post

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = "blogs/index.html"

    def get_queryset(self):
        return Post.published.select_related("author", "author__profile").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.get_queryset()
        paginator = Paginator(post_list, per_page=10)
        page_number = self.request.GET.get("page")
        posts = paginator.get_page(page_number)

        tags = Tag.objects.all()

        context["posts"] = posts
        context["tags"] = tags
        return context


class AboutView(TemplateView):
    template_name = "about.html"


class SearchView(TemplateView):
    template_name = "blogs/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        results = None
        if query:
            results = Post.published.filter(title__icontains=query)

        context["query"] = query
        context["results"] = results
        return context


class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new post."""

    model = Post
    form_class = PostModelForm
    success_message = "The post has been created successfully."
    template_name = "blogs/post_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = Post.Status.PUBLISHED
        return super().form_valid(form)


class PostDetailView(DetailView, FormView):
    """
    Detail view for displaying a post and handling comment submission.
    """

    model = Post
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    form_class = CommentModelForm
    template_name = "blogs/post_detail.html"

    def get_queryset(self):
        return Post.published.all()

    def dispatch(self, request, *args, **kwargs):
        # Check if the request method is POST and the user is authenticated
        if request.method == "POST" and not request.user.is_authenticated:
            # Redirects to the login page, and then back to another URL after a successful login.
            # Returns the path, plus an appended query string, if applicable.
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        related_tags = post.tags.all()
        context["form"] = self.get_form()
        context["post_likes"] = post.get_likes()
        context["likes_count"] = post.get_likes_count()
        context["comments"] = post.get_comments()
        context["total_comments"] = post.get_total_comments()
        context["related_tags"] = related_tags
        return context

    def form_valid(self, form):
        """
        Save the comment associated with the post and the logged-in user.
        """
        comment = form.save(commit=False)
        comment.post = self.get_object()
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        """URL to redirect to after successfully submitting a comment."""
        post = self.get_object()
        return post.get_absolute_url()


class PostUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Post
    context_object_name = "post"
    form_class = PostModelForm
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    success_message = "The post has been updated successfully."
    template_name = "blogs/post_update.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class PostDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Post
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    success_message = "The post has been deleted successfully."
    success_url = reverse_lazy("blogs:index")
    template_name = "blogs/post_delete.html"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentModelForm
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/comment_update.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def form_valid(self, form):
        form.instance.edited = True
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    context_object_name = "comment"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/comment_delete.html"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, id=pk)
        user = request.user
        if user in post.get_likes():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        likes_count = post.get_likes_count()
        return JsonResponse({"liked": liked, "likes_count": likes_count})
