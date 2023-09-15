from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import PostModelForm, CommentModelForm
from .models import Post, Comment

User = get_user_model()


class IndexView(TemplateView):
    template_name = "blogs/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = Post.published.all()
        paginator = Paginator(post_list, per_page=10)
        page_number = self.request.GET.get("page")
        posts = paginator.get_page(page_number)
        context["posts"] = posts
        return context


class AboutView(TemplateView):
    template_name = "about.html"


class SearchView(TemplateView):
    template_name = "blogs/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        if query:
            results = Post.published.filter(title__icontains=query)
        context["results"] = results
        return context


class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostModelForm
    success_message = "The post has been created successfully."
    template_name = "blogs/post_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = Post.Status.PUBLISHED
        return super().form_valid(form)


class CommentGetView(DetailView):
    model = Post
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/post_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = post.comments.filter(active=True)
        total_comments = comments.count()
        context["form"] = CommentModelForm()
        context["comments"] = comments
        context["total_comments"] = total_comments
        return context


class CommentPostView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Post
    form_class = CommentModelForm
    slug_field = "slug"
    slug_url_kwarg = "post_slug"
    template_name = "blogs/post_detail.html"

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.get_object()
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        post = self.get_object()
        return reverse(
            "blogs:post-detail",
            kwargs={"username": post.author.username, "post_slug": post.slug},
        )


class PostDetailView(DetailView):
    def get(self, request, *args, **kwargs):
        view = CommentGetView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPostView.as_view()
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


class LikeAddView(LoginRequiredMixin, View):
    def post(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=post_slug)

        is_disliked = False
        for dislike in post.dislikes.all():
            if dislike == self.request.user:
                is_disliked = True
                break

        # if post is already disliked, the dislike will be removed and the post will be liked
        # because a user can not like and dislike the same post at same time
        if is_disliked:
            post.dislikes.remove(self.request.user)

        is_liked = False
        for like in post.likes.all():
            if like == self.request.user:
                is_liked = True
                break

        if not is_liked:  # not liked the post
            post.likes.add(self.request.user)

        if is_liked:  # already liked the post
            post.likes.remove(self.request.user)

        return redirect(post.get_absolute_url())


class DislikeAddView(LoginRequiredMixin, View):
    def post(self, request, post_slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=post_slug)

        is_liked = False
        for like in post.likes.all():
            if like == self.request.user:
                is_liked = True
                break

        if is_liked:
            post.likes.remove(self.request.user)

        is_disliked = False
        for dislike in post.dislikes.all():
            if dislike == self.request.user:
                is_disliked = True
                break

        if not is_disliked:
            post.dislikes.add(self.request.user)

        if is_disliked:
            post.dislikes.remove(self.request.user)

        return redirect(post.get_absolute_url())
