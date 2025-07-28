from rest_framework import serializers
from .models import AboutUs, ContactUs, ContactSubmission

class AboutUsSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = AboutUs
        fields = '__all__'

    def get_content(self, obj):
        request = self.context.get('request')
        content = obj.content
        if request:
            full_media_url = request.build_absolute_uri('/media/')
            content = content.replace('src="/media/', f'src="{full_media_url}')
        return content

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'
        read_only_fields = ('last_updated',)

class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = '__all__'
        read_only_fields = ('submitted_at', 'is_read')