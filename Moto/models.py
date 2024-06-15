from django.db import models

from User.models import User


# Create your models here.


class Moto(models.Model):
    name = models.CharField(max_length=255,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField(default=1)
    available = models.PositiveIntegerField(default=1)


