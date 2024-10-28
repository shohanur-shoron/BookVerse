from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} added by {self.added_by}"


class Author(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='author_images/', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    addedBy = models.ForeignKey(User, related_name='addedBy', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name} added by {self.addedBy}"


class Book(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    authors = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_views = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0)
    suggestions = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    link_clicked = models.PositiveIntegerField(default=0)
    likes_counter = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    published_time = models.DateField(auto_now=False, auto_now_add=True)
    pages = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=100, blank=True, null=True)
    chapters = models.PositiveIntegerField(default=0)
    favorites_chapters = models.PositiveIntegerField(default=0)
    favorites_quotes = models.TextField(blank=True, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    reading_level = models.CharField(max_length=50, blank=True, null=True)
    best_character = models.CharField(max_length=100, blank=True, null=True)
    awards = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=50,
                              choices=[('Hardcover', 'Hardcover'), ('Paperback', 'Paperback'), ('eBook', 'eBook')],
                              blank=True, null=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.book.name


class ReadingStatus(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('to_read', 'To Read'),
        ('reading', 'Currently Reading'),
        ('completed', 'Completed')
    ])
    current_page = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
