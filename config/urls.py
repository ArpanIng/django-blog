from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from blogs.feeds import PostsFeeds, AtomSiteNewsFeed
from blogs.sitemaps import PostSitemap

sitemaps = {
    "posts": PostSitemap,
}

context = {
    "sitemaps": sitemaps,
}

from accounts.views import ContactFormView, ContactSuccess
from blogs.views import AboutView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.user_urls", namespace="users")),
    path("", include("blogs.urls", namespace="blogs")),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("contact/success/", ContactSuccess.as_view(), name="contact_success"),
    path("account/", include("accounts.urls", namespace="accounts")),
    path("tinymce/", include("tinymce.urls")),
    path("feed/rss", PostsFeeds(), name="post_feed"),
    path("feed/atom", AtomSiteNewsFeed()),
    path("sitemap.xml", sitemap, context, name="django.contrib.sitemaps.views.sitemap"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "blogs.error_handlers.handler404"
handler403 = "blogs.error_handlers.handler403"

if settings.DEBUG:

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
