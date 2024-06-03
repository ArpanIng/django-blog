from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import FormView

from blogs.models import Post

from .forms import (
    ContactForm,
    CustomUserCreationForm,
    ProfileUpdateForm,
    UserUpdateForm,
)
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


class CustomPasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")
    template_name = "accounts/registration/password_change_form.html"


class CustomPasswordChangeDoneView(
    LoginRequiredMixin,
    auth_views.PasswordResetDoneView,
):
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


class SettingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "user_setting"
        return context


class UserProfileView(generic.DetailView):
    model = User
    context_object_name = "user"
    template_name = "accounts/profile.html"

    def get_object(self):
        username = self.kwargs.get("username")
        return get_object_or_404(User, username=username)

    def get_template_names(self):
        if self.request.htmx:
            return "blogs/partials/post_list.html"
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        posts = Post.published.filter(author=user).select_related(
            "author", "author__profile"
        )
        paginator = Paginator(posts, per_page=10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        profile = get_object_or_404(Profile, user=user)

        context["page_obj"] = page_obj
        context["posts"] = page_obj.object_list
        context["profile"] = profile
        context["username"] = self.kwargs.get("username")
        context["followers_count"] = profile.get_followers_count()
        context["followings"] = profile.get_followings()
        context["page_name"] = "user_home"
        return context


class UserAboutView(generic.TemplateView):
    template_name = "accounts/user_about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)

        followers_count = user.profile.get_followers_count()
        following_count = user.profile.get_followings_count()

        context["user"] = user
        context["profile"] = user.profile
        context["followers_count"] = followers_count
        context["following_count"] = following_count
        context["page_name"] = "user_about"
        return context


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
            messages.success(request, "Your profile has been successfully updated.")
            return redirect("users:profile", request.user.username)

        context = {
            "u_form": u_form,
            "p_form": p_form,
        }
        return render(request, "accounts/profile_edit.html", context)


class FollowToggleView(generic.View):
    """
    Toggle follow/unfollow functionality for a user profile.
    If the user is already following the profile, it unfollows; otherwise, it follows.
    """

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "message": "Invalid request method."})

    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            profile = get_object_or_404(Profile, user_id=pk)
            profile_url = reverse(
                "users:profile", kwargs={"username": profile.user.username}
            )
            login_url = reverse("accounts:login")
            redirect_url = f"{login_url}?next={profile_url}"
            return HttpResponseRedirect(redirect_url)

        user_to_follow = get_object_or_404(Profile, user_id=pk)
        user_profile = request.user.profile
        is_following = False

        if user_to_follow in user_profile.get_followings():
            user_profile.follows.remove(user_to_follow)
            message = f"You have unfollowed {user_to_follow.user.get_full_name()}."
        else:
            user_profile.follows.add(user_to_follow)
            is_following = True
            message = f"You are now following {user_to_follow.user.get_full_name()}."

        response_data = {
            "success": True,
            "is_following": is_following,
            "message": message,
            "followers_count": user_to_follow.get_followers_count(),
        }
        return JsonResponse(response_data)


class ProfileBaseView(generic.ListView):
    model = Profile

    def get_profile(self):
        username = self.kwargs.get("username")
        return get_object_or_404(Profile, user__username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_profile()
        context["profile"] = profile
        context["followers_count"] = profile.get_followers_count()
        context["following_count"] = profile.get_followings_count()
        return context


class FollowingListView(ProfileBaseView):
    """Displays the list of profiles followed by a user."""

    context_object_name = "followings"
    template_name = "accounts/profile_follow_list.html"

    def get_queryset(self):
        return self.get_profile().get_followings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "user_following"
        return context


class FollowersListView(ProfileBaseView):
    """isplays the list of followers of a user."""

    context_object_name = "followers"
    template_name = "accounts/profile_follow_list.html"

    def get_queryset(self):
        return self.get_profile().get_followers()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "user_followers"
        return context


class ContactSuccess(generic.TemplateView):
    """
    A template view to display a success message after submitting a contact form.
    """

    template_name = "contact/success.html"


class ContactFormView(FormView):
    """A view for displaying and submitting a contact form."""

    form_class = ContactForm
    template_name = "contact/contact_form.html"
    success_url = reverse_lazy("contact_success")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        email_message = form.cleaned_data.get("message")

        send_mail(
            subject=subject,
            message=email_message,
            from_email=email,
            recipient_list=[settings.NOTIFY_EMAIL],
        )
        return super(ContactFormView, self).form_valid(form)
