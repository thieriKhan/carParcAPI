import random

from django.contrib import admin
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser

from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.utils import translation
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from rest_framework.utils import json

from authentication.utils import generate_otp


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

    email = models.EmailField(unique=True, null=False, blank=False )

    language = models.CharField(max_length=2, default='en')





    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f'{self.username} '



@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "http://localhos:8100/auth/reset"

    }

    # render email text
    # otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    otp = generate_otp()
    reset_password_token.key = otp
    reset_password_token.save()
    link =instance.request.build_absolute_uri("http://localhost:4000/auth/change-password?otp="+otp+"&email="+reset_password_token.user.email)
    user = User.objects.filter(email=reset_password_token.user.email).first()
    print(reset_password_token.user.email)
    username=user.first_name + " " + user.last_name
    # print(username)


    email_plaintext_message = f"Hello {username} ton code OTP est {otp} ou cliquer sur le liens pour refaire votre pass: \n {link}"

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Car park"),

        # message:
        email_plaintext_message,
        # from:
        "no-reply.carparc@gmail.com",
        # to:
        [reset_password_token.user.email]
    )


    msg.send()
