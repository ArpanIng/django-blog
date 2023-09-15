"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

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


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blogs.urls", namespace="blogs")),
    path("", include("accounts.user_urls", namespace="users")),
    path("account/", include("accounts.urls", namespace="accounts")),
    path("feed/rss", PostsFeeds(), name="post_feed"),
    path("feed/atom", AtomSiteNewsFeed()),
    path("sitemap.xml", sitemap, context, name="django.contrib.sitemaps.views.sitemap"),
]

handler404 = "blogs.error_handlers.handler404"
handler403 = "blogs.error_handlers.handler403"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
