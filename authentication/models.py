from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from invent.models import Baseclass   # BaseModel from inventory app


class RoleChoices(models.TextChoices):

    USER = 'User', 'User'
    ADMIN = 'Admin', 'Admin'


class Profile(AbstractUser):

    phone = PhoneNumberField(unique=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices)
    
    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Profiles'
        verbose_name_plural = 'Profiles'


class OTP(Baseclass):

    profile = models.OneToOneField('Profile', on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)

    def __str__(self):
        return f'{self.profile.first_name} otp'

    class Meta:
        verbose_name = 'OTPs'
        verbose_name_plural = 'OTPs'


class TempOTP(Baseclass):

    phone = models.CharField(max_length=13)
    otp = models.CharField(max_length=4)

    def __str__(self):
        return f'{self.phone} otp'

    class Meta:
        verbose_name = 'Temp OTPs'
        verbose_name_plural = 'Temp OTPs'