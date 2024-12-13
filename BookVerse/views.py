from django.shortcuts import render, redirect, get_object_or_404
from books.models import Book


def index(request):
    return render(request, "signupAndLogin/ok.html")

def mainHomePage(request):
    books = Book.objects.all()

    context = {
        'books': books,
        'favorite_books': [],
    }

    if request.user.is_authenticated:
        favorite_books = Book.objects.filter(favorite__user=request.user)
        context = {
            'books': books,
            'favorite_books': favorite_books,
        }

    return render(request, "homePages/mainHomePage.html", context)