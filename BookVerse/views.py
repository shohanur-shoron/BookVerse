from django.shortcuts import render, redirect, get_object_or_404
from books.models import Book


def index(request):
    return render(request, "signupAndLogin/ok.html")

def mainHomePage(request):
    return render(request, "homePages/mainHomePage.html")