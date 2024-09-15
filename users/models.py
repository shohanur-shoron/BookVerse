from django.contrib.auth.models import User
from django.db import models
from books.models import Category

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='proPic', null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)

    is_user = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)

    total_reviews = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    interests = models.ManyToManyField(Category, related_name='interests', blank=True)

    def __str__(self):
        return self.user.first_name
