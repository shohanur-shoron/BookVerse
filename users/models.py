from django.contrib.auth.models import User
from django.db import models
from books.models import Category
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='proPic/original', null=True, blank=True)
    resized_image = models.ImageField(upload_to='proPic/resized/', blank=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=20, null=True, blank=True)

    is_user = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)

    total_reviews = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)

    interests = models.ManyToManyField(Category, related_name='interests', blank=True, null=True)

    def __str__(self):
        return self.user.first_name

    def save(self, *args, **kwargs):
        # Check if this is an update operation
        if self.pk:
            # Get the old instance from the database
            old_instance = Profile.objects.get(pk=self.pk)
            # If the image has changed, delete the old image files
            if old_instance.image != self.image:
                self.delete_image_files(old_instance)

        super().save(*args, **kwargs)

        if self.image:
            resized = self.resize_image(self.image)
            self.resized_image.save(resized.name, resized, save=False)
            super().save(update_fields=['resized_image'])

    def delete(self, *args, **kwargs):
        # Delete image files before deleting the model instance
        self.delete_image_files(self)
        super().delete(*args, **kwargs)

    def delete_image_files(self, instance):
        # Delete original image
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

        # Delete resized image
        if instance.resized_image:
            if os.path.isfile(instance.resized_image.path):
                os.remove(instance.resized_image.path)

    @staticmethod
    def resize_image(pro_image, width=100):
        img = Image.open(pro_image.path)
        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio)
        img = img.resize((width, new_height), Image.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)

        return InMemoryUploadedFile(output, 'ImageField',
                                    f"{pro_image.name.split('.')[0]}_resized.jpg",
                                    'image/jpeg', output.getbuffer().nbytes, None)