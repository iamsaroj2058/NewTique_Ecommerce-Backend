from django.urls import path, include
from .views import AboutUsDetailView, ContactUsDetailView, ContactSubmissionCreateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('about-us/', AboutUsDetailView.as_view(), name='about-us'),
    path('contact-us/', ContactUsDetailView.as_view(), name='contact-us'),
    path('contact/submit/', ContactSubmissionCreateView.as_view(), name='contact-submit'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)