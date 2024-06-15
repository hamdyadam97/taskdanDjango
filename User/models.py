import re
import uuid
import datetime
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager as DjangoUserManager, Group, Permission
from django.db.models import Count, Q, F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


def send_email(subject, email, body, from_email=settings.DEFAULT_FROM_EMAIL):
    msg = EmailMultiAlternatives()
    msg.from_email = from_email
    msg.subject = subject.strip()
    msg.body = body
    msg.attach_alternative(body, "text/html")
    if isinstance(email, list):
        msg.to = email
    else:
        msg.to = [email]
    msg.send()
def validate_username_user(username):
    pattern = re.compile("^(?=[a-zA-Z0-9._]{3,20}$)(?!.*[_.]{2})[^_.].*[^_.]$")
    if pattern.match(username):
        return username
    else:
        raise ValidationError("The username field should be between 3 and 20 characters in length and may contain "
                              "characters, numbers, or special characters (_.), but not at the beginning or end.")


class UserManager(DjangoUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

    def get_by_natural_key(self, email):
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': email})


def upload_to_profile_pic(instance, filename):
    return f'uploads/profile/{uuid.uuid4()}/{filename}'


class User(AbstractBaseUser, PermissionsMixin):
    display_name = models.CharField(max_length=150)
    email = models.EmailField(_('email address'),)
    id_national = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=20, blank=True, null=True)
    account_moto = models.IntegerField(null=True)
    file = models.FileField(null=True, blank=True,upload_to=upload_to_profile_pic)
    rules_agreed = models.BooleanField(default=False)
    agreement = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user'
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_deactivated = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_online = models.DateTimeField(_('last online'), blank=True, null=True)
    is_set_password = models.BooleanField(default=True)
    # This field is for Social users that didn't edit their profile, mainly Apple Users for now.
    is_new_user = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)
    objects = UserManager()
    is_notification_seen = models.BooleanField(default=True)
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    is_phone_verified = models.BooleanField(default=False)
    phone_country_code = models.CharField(max_length=20, blank=True, null=True)
    phone_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.display_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @cached_property
    def token(self):
        return RefreshToken.for_user(self)

    def send_email_verification(self, force_new_code=False):
        if force_new_code or self.email_verification_code is None:
            self.email_verification_code = get_random_string(6, '0123456789')
            self.save()

        context = {
            'display_name': self.display_name,
            'verification_code': self.email_verification_code
        }
        body = render_to_string('users/email_verification.html', context)
        send_email(
            subject='Please confirm your email',
            body=body,
            email=self.email
        )

@receiver(post_save, sender=User)
def send_email_verification(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    print('ssssssssssssssssssssssssssssssssssssssssssssssssss')
    if created and not instance.is_email_verified and not instance.phone_number:
        instance.send_email_verification()