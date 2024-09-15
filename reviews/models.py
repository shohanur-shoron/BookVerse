from django.contrib.auth.models import User
from django.db import models

from books.models import Book


class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} commented on {self.book.name}"
