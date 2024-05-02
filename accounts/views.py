from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from blogs.models import Post

from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile

User = get_user_model()


class CustomLoginView(auth_views.LoginView):
    """
    Custom login view.
    """

    template_name = "accounts/registration/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(auth_views.LogoutView):
    """
    Custom logout view.
    """

    template_name = "accounts/registration/logout.html"


class CustomSignupView(generic.View):
    """
    Custom sign-up view based on Django's generic CreateView.
    It uses the CustomUserCreationForm for user registration.
    """

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/registration/signup.html"

    def dispatch(self, request, *args, **kwargs):
        # If the user is already authenticated, redirects them to the index page.
        if request.user.is_authenticated:
            return redirect("blogs:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created sucessfully!")
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form})


class SettingView(generic.TemplateView):
    template_name = "accounts/settings.html"


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")
    template_name = "accounts/registration/password_change_form.html"


class CustomPasswordChangeDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/registration/password_change_done.html"


class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = "accounts/registration/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    template_name = "accounts/registration/password_reset_form.html"


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/registration/password_reset_done.html"


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy("accounts:password_reset_complete")
    template_name = "accounts/registration/password_reset_confirm.html"


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/registration/password_reset_complete.html"


class ProfileView(generic.TemplateView):
    template_name = "accounts/profile.html"
    # template_name = "accounts/followers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        followers = user.followers.all()
        followers_count = followers.count()
        post_list = Post.published.filter(author=user)
        paginator = Paginator(post_list, per_page=10)
        page_number = self.request.GET.get("page")
        posts = paginator.get_page(page_number)
        context["posts"] = posts
        context["user"] = user
        context["followers"] = followers
        context["followers_count"] = followers_count
        context["page_name"] = "Home"
        return context


class UserAboutView(generic.TemplateView):
    template_name = "accounts/user_about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        followers = user.followers.all()
        followers_count = followers.count()
        post_list = Post.published.filter(author=user)
        paginator = Paginator(post_list, per_page=10)
        page_number = self.request.GET.get("page")
        posts = paginator.get_page(page_number)
        context["posts"] = posts
        context["user"] = user
        context["followers"] = followers
        context["followers_count"] = followers_count
        context["page_name"] = "Home"
        return context


class Followers(generic.TemplateView):
    template_name = "accounts/followers.html"


class AddFollowView(generic.TemplateView):
    def post(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        profile = get_object_or_404(Profile, user=username)
        print("---------")
        print(profile)
        print("---------")


class ProfileEditView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        u_form = UserUpdateForm(instance=self.request.user)
        p_form = ProfileUpdateForm(instance=self.request.user.profile)

        context = {
            "u_form": u_form,
            "p_form": p_form,
        }
        return render(request, "accounts/profile_edit.html", context)

    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(self.request.POST, instance=self.request.user)
        p_form = ProfileUpdateForm(
            self.request.POST,
            self.request.FILES,
            instance=self.request.user.profile,
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("users:profile", request.user.username)

        context = {
            "u_form": u_form,
            "p_form": p_form,
        }
        return render(request, "accounts/profile_edit.html", context)


# class FollowUserView(LoginRequiredMixin, generic.View):
#     def post(self, request, pk, *args, **kwargs):
#         profile = Profile.objects.get(pk=pk)
#         profile.followers.add(self.request.user)
#         return redirect()

# class FollowUserView(LoginRequiredMixin, generic.View):
#     def post(self, request, username, *args, **kwargs):
#         user_to_followe = get_object_or_404(User, username=username)
#         user_profile = request.user.profile

#         user_profile.foll


class FollowerListView(generic.View):
    def get(self, request, *args, **kwargs):
        template_name = "accounts/followers.html"
        return render(request, template_name)


# class FollowerListView(generic.ListView):
#     model = Profile
#     template_name = "accounts/followers.html"

#     def get_queryset(self):
#         return super().get_queryset().filter(followers=)


# class AddFollowView(LoginRequiredMixin, generic.View):
#     def post(self, request, username, *args, **kwargs):
#         profile = get_object_or_404(Profile, user=user)
#         print("-----------")
#         print(profile)
#         print("-----------")
#         # profile.followers.add(self.request.user)
#         # return redirect(profile.ge)


# @login_required
# def follow_user(request, username):
#     if request.method == 'POST':
#         user_to_follow = get_object_or_404(CustomUser, username=username)
#         user_profile = request.user.profile

#         if user_to_follow != request.user:
#             user_to_follow.profile.followers.add(request.user)
#             messages.success(request, f'You are now following {user_to_follow.username}')
#         else:
#             messages.warning(request, 'You cannot follow yourself.')

#     return redirect('users:profile', username=username)

# @login_required
# def unfollow_user(request, username):
#     if request.method == 'POST':
#         user_to_unfollow = get_object_or_404(CustomUser, username=username)
#         user_profile = request.user.profile

#         if user_to_unfollow.profile.followers.filter(username=request.user.username).exists():
#             user_to_unfollow.profile.followers.remove(request.user)
#             messages.success(request, f'You have unfollowed {user_to_unfollow.username}')
#         else:
#             messages.warning(request, f'You were not following {user_to_unfollow.username}')

#     return redirect('users:profile', username=username)
