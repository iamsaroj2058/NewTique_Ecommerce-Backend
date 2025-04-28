# """Models for the user management."""

# from django.contrib.auth.models import AbstractUser, BaseUserManager
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from phonenumber_field.modelfields import PhoneNumberField

# # from accounts.api.otp import OTP

# from django.core import validators
# from django.core.exceptions import ValidationError
# from django.utils.deconstruct import deconstructible
# from django.utils.translation import gettext_lazy as _
# from phonenumber_field.phonenumber import to_python
# from phonenumbers.phonenumberutil import is_possible_number


# def validate_phone_number(phone, country=None):
#     """
#     Validate that the phone number value is valid or not.

#     Args:
#         phone (string): value to be validated.
#         country (any): region for the passed phone number.

#     Raises:
#         ValidationError: error with msg.

#     """
#     from account.enums import AccountErrorCode

#     phone_number = to_python(phone, country)
#     if (
#         phone_number
#         and not is_possible_number(phone_number)
#         or not phone_number.is_valid()
#     ):
#         raise ValidationError(
#             "The phone number entered is not valid.", code=AccountErrorCode.INVALID
#         )
#     return phone_number

# class ValidPhoneNumberField(PhoneNumberField):

#     """Class to validate phone number."""

#     default_validators = [validate_phone_number]


# class CustomUserManager(BaseUserManager):

#     """Custom manager for the User model to handle user creation."""

#     def create_user(self, email, password, **extra_fields):
#         """
#         Create and return a user with an email and password.

#         Args:
#             email (str): The email address for the user.
#             password (str): The password for the user.
#             **extra_fields: Additional fields to set on the user.

#         Returns:
#             User

#         Raises:
#             ValueError: If no password is provided.

#         """

#         if not email:
#             raise ValueError("The Email field must be set")

#         if not password:
#             raise ValueError("The Password field must be set")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         """
#         Create and return a superuser with an email and password.

#         Args:
#             email (str): The email address for the superuser.
#             password (str, optional): The password for the superuser.
#             **extra_fields: Additional fields to set on the superuser.

#         Returns:
#             User

#         Raises:
#             ValueError: If `is_staff` or `is_superuser` is not set to True.

#         """

#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")

#         return self.create_user(email, password, **extra_fields)


# class User(AbstractUser):

#     """
#     Custom user model extending the AbstractUser with additional fields.

#     Attributes:
#         email (EmailField: The email of the user.
#         full_name (CharField): The name of the user.
#         phone_number (CharField): The phone number of the user.
#         citizenship_number (CharField): The citizenship number of the user.
#         created_at (DateTimeField): The timestamp when the user was created.
#         created_by (ForeignKey): Reference to the user who created this user.
#         user_type (CharField): The type of user (e.g., Proponent).
#         ministry (ForeignKey): Reference to the ministry of user.

#     """

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = []

#     username = None

#     email = models.EmailField(unique=True, blank=False, null=False)
#     full_name = models.CharField(blank=False, null=False)
#     phone_number = ValidPhoneNumberField(_("Phone Number"), unique=True)
#     is_active = models.BooleanField(
#         _("active"),
#         default=False,
#         help_text=_(
#             "Designates whether this user should be treated as active. "
#             "Unselect this instead of deleting accounts."
#         ),
#     )
#     otp = models.CharField(max_length=6, null=True, blank=True)
#     otp_generate_time = models.DateTimeField(auto_now_add=True)
#     otp_counter = models.PositiveIntegerField(default=0)
#     otp_verified = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     def get_full_name(self):
#         """Retreive full name of the user."""
#         return self.full_name

#     def clean(self):
#         """Validate to ensure phone_number and email uniquenes."""
#         if not self.phone_number and not self.email:
#             raise ValidationError("Either an email or phone number must be provided.")
   
#     def generate_static_otp(self):
#         """Generate a static OTP for user registration with expiration logic."""
#         self.otp = "123456"
#         self.otp_generate_time = timezone.now()
#         self.otp_verified = False
#         self.save()
#         return self.otp

#     # def validate_otp(self, otp):
#     #     """To validate received OTP."""

#     #     if self.otp_verified:
#     #         return (False, "OTP is already verified")

#     #     five_minutes_ago = make_aware(
#     #         datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
#     #     )
#     #     if not self.otp:
#     #         return (False, "OTP is already used")
#     #     if self.otp_generate_time < five_minutes_ago:
#     #         return (False, "The OTP is out of date")
#     #     if self.otp != otp:
#     #         return (False, "OTP is not valid")

#     #     self.otp_verified = True
#     #     self.save()
#     #     return (True, otp)

#     # def generate_otp(self, action, phone_number=None, request=None, medium="sms"):
#     #     """To generate OTP and call send otp method."""

#     #     check_limit = True
#     #     if request:
#     #         check_limit = rate_limiting(request)["status"]

#     #     if check_limit:
#     #         self.otp_counter += 1

#     #         if phone_number:
#     #             ph_number = phone_number
#     #         else:
#     #             ph_number = self.phone_number

#     #         otp = OTP.generateOTP(ph_number, self.otp_counter)

#     #         self.otp_generate_time = make_aware(datetime.now())
#     #         self.otp_verified = False
#     #         self.otp = otp
#     #         self.save()
#     #         OTP.sendOTP(str(ph_number), otp, action, medium)
#     #         return otp

#     #     raise exceptions.APIRateLimitException()

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver 
from django.urls import reverse 
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

class CustomUserManager(BaseUserManager): 
    def create_user(self, email, password=None, **extra_fields ): 
        if not email: 
            raise ValueError('Email is a required field')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email, password=None, **extra_fields): 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    birthday = models.DateField(null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, *args, **kwargs):
    sitelink = "http://localhost:5173/"
    token = "{}".format(reset_password_token.key)
    full_link = str(sitelink)+str("password-reset/")+str(token)

    print(token)
    print(full_link)

    context = {
        'full_link': full_link,
        'email_adress': reset_password_token.user.email
    }

    html_message = render_to_string("backend/email.html", context=context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(
        subject = "Request for resetting password for {title}".format(title=reset_password_token.user.email), 
        body=plain_message,
        from_email = "sender@example.com", 
        to=[reset_password_token.user.email]
    )

    msg.attach_alternative(html_message, "text/html")
    msg.send()