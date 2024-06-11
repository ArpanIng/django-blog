from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.list import ListView
from taggit.models import Tag

from .forms import CommentModelForm, PostModelForm
from .models import Comment, Post

User = get_user_model()


class PostListView(ListView):
    model = Post
    paginate_by = 10
    context_object_name = "posts"
    template_name = "blogs/index.html"

    def get_queryset(self):
        queryset = (
            Post.published.select_related("author", "author__profile")
            .prefetch_related("tags")
            .all()
        )

        # filter posts based on tag
        tag = self.kwargs.get("tag_slug")
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        # filter posts based on search params
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(title__icontains=query)

        return queryset

    def get_template_names(self):
        if self.request.htmx:
            return "blogs/partials/post_list.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = Tag.objects.all()
        context["tags"] = tags
        context["tag"] = self.kwargs.get("tag_slug")
        context["query"] = self.request.GET.get("q")
        return context


class AboutView(TemplateView):
    template_name = "about.html"


class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for creating a new post."""

    model = Post
    form_class = PostModelForm
    success_message = "The post has been created successfully."
    template_name = "blogs/post_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        if self.object.status == Post.Status.DRAFT:
            return redirect("accounts:dashboard")
        return response


class PostDetaillView(DetailView):
    """View for displaying a post."""

    model = Post
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/post_detail.html"

    def get_queryset(self):
        return Post.published.select_related("author__profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        related_tags = post.tags.all()
        context["form"] = CommentModelForm()
        context["post_likes"] = post.get_likes()
        context["likes_count"] = post.get_likes_count()
        context["comments"] = post.get_comments()
        context["total_comments"] = post.get_total_comments()
        context["related_tags"] = related_tags
        return context


class PostCommentFormView(SingleObjectMixin, FormView):
    """
    View for handling the submission of comments on a post.
    """

    model = Post
    form_class = CommentModelForm
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/post_detail.html"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("accounts:login")
            redirect_url = f"{login_url}?next={request.path}"
            return HttpResponseRedirect(redirect_url)
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Save the comment associated with the post and the logged-in user.
        """
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        """URL to redirect to after successfully submitting a comment."""
        post = self.get_object()
        return post.get_absolute_url()


class PostView(View):
    """
    View for handling both GET and POST requests for a post.
    """

    def get(self, request, *args, **kwargs):
        view = PostDetaillView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostCommentFormView.as_view()
        return view(request, *args, **kwargs)


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

    def get_success_url(self):
        post = self.get_object()
        if post.status == Post.Status.DRAFT:
            return reverse("accounts:dashboard")
        else:
            return post.get_absolute_url()


class PostDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Post
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    success_message = "The post has been deleted successfully."
    success_url = reverse_lazy("accounts:dashboard")
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
