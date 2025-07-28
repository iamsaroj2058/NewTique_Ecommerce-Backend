from django.contrib import admin
from .models import AboutUs, ContactUs, ContactSubmission
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms

class AboutUsAdminForm(forms.ModelForm):
    class Meta:
        model = AboutUs
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(config_name='extends'),
        }

class ContactUsAdminForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(config_name='extends'),
        }

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    form = AboutUsAdminForm
    list_display = ('title', 'is_active', 'last_updated')
    list_editable = ('is_active',)

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    form = ContactUsAdminForm
    list_display = ('title', 'is_active', 'last_updated')
    list_editable = ('is_active',)

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at', 'is_read')
    list_filter = ('is_read', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('submitted_at',)