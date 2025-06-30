from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailVerification, CustomUser
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def create_email_verification(sender, instance, created, **kwargs):
    if created and not instance.is_verified:
        verification = EmailVerification.objects.create(user=instance)
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{verification.token}/"
        
        context = {
            'verification_link': verification_link,
            'user': instance
        }
        
        html_message = render_to_string("email_verification.html", context)
        plain_message = strip_tags(html_message)

        msg = EmailMultiAlternatives(
            subject="Verify Your Email",
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email]
        )
        msg.attach_alternative(html_message, "text/html")
        
        try:
            msg.send()
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")