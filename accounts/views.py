from django.contrib import messages

from django.contrib.auth import views, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views import generic

from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile

from blogs.models import Post

User = get_user_model()


class CustomLoginView(views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(views.LogoutView):
    pass


class CustomSignupView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("blogs:index")
        return super().dispatch(request, *args, **kwargs)


class SettingView(generic.TemplateView):
    template_name = "accounts/settings.html"


class CustomPasswordChangeView(views.PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")
    template_name = "accounts/password_change_form.html"


class CustomPasswordChangeDoneView(views.PasswordResetDoneView):
    template_name = "accounts/password_change_done.html"


class CustomPasswordResetView(views.PasswordResetView):
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    template_name = "accounts/password_reset_form.html"


class CustomPasswordResetDoneView(views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(views.PasswordResetConfirmView):
    success_url = reverse_lazy("accounts:password_reset_complete")
    template_name = "accounts/password_reset_confirm.html"


class CustomPasswordResetCompleteView(views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class ProfileView(generic.TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        post_list = Post.published.filter(author=user)
        paginator = Paginator(post_list, per_page=2)
        page_number = self.request.GET.get("page")
        posts = paginator.get_page(page_number)
        context["posts"] = posts
        context["user"] = user
        return context


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
