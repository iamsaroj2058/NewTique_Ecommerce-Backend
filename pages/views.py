from rest_framework import generics
from .models import AboutUs, ContactUs, ContactSubmission
from .serializers import AboutUsSerializer, ContactUsSerializer, ContactSubmissionSerializer
from rest_framework.permissions import AllowAny


class AboutUsDetailView(generics.RetrieveUpdateAPIView):
    queryset = AboutUs.objects.filter(is_active=True)
    serializer_class = AboutUsSerializer

    def get_object(self):
        return AboutUs.objects.first()

class ContactUsDetailView(generics.RetrieveUpdateAPIView):
    queryset = ContactUs.objects.filter(is_active=True)
    serializer_class = ContactUsSerializer

    def get_object(self):
        return ContactUs.objects.first()

class ContactSubmissionCreateView(generics.CreateAPIView):
    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer
    permission_classes = [AllowAny]