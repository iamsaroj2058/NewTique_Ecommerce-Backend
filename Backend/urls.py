"""
URL configuration for Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from Backend import views
from django.conf import settings
from django.conf.urls.static import static
from knox import views as knox_views


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("about-us/", views.aboutUs),
    # path("Login/", knox_views.LoginView(),name='knox_login'),
    path('store/', include('store.urls')), 
    path('account/', include('account.api.urls')), 
    path('logout/',knox_views.LogoutView.as_view(), name='knox_logout'), 
    path('logoutall/',knox_views.LogoutAllView.as_view(), name='knox_logoutall'), 
    path('api/password_reset/',include('django_rest_passwordreset.urls', namespace='password_reset')),
    path("api/", include("account.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

