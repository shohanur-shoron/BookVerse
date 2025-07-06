from django.db import models
from django.contrib.auth.models import User

from book.models import Category


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='proPic/original', null=True, blank=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=20, null=True, blank=True)

    is_user = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)

    interests = models.ManyToManyField(Category, related_name='interests', blank=True, null=True)

    total_reviews = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    def __str__(self):
        return self.user.first_name
