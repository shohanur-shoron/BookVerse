from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=False)

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
    pages = models.CharField(max_length=80, null=True, blank=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    chapters = models.CharField(max_length=50, null=True, blank=True)
    favorites_chapters = models.CharField(max_length=50, null=True, blank=True)
    favorites_quotes = models.TextField(blank=True, null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    best_character = models.CharField(max_length=100, blank=True, null=True)
    awards = models.TextField(blank=True, null=True)
    format = models.CharField(
        max_length=50,
        choices=[('Hardcover', 'Hardcover'), ('Paperback', 'Paperback'), ('eBook', 'eBook')],
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.pk})
    def __str__(self):
        return f'{self.name} by {self.authors.name} book'


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


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    ongoing = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.is_valid}'

class MyEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.event.name} "


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    textSentimentScore = models.FloatField(null=True, blank=True)
    sentimentCategory = models.CharField(max_length=50, null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.book.name}'


class RecentlyViewedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True) # auto_now updates time on every save

    class Meta:
        ordering = ['-timestamp'] # Show newest first by default
        # Ensure a user doesn't have the same book listed multiple times
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} viewed {self.book.name} at {self.timestamp}"
