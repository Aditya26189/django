# filepath: /c:/Users/LawLight/OneDrive/Desktop/storefront/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    def send_verification_email(self):
        subject = 'Verify your email'
        message = render_to_string('email/verification_email.html', {
            'user': self,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
        })
        send_mail(subject, message, 'no-reply@example.com', [self.email])

    def __str__(self):
        return self.username
    

