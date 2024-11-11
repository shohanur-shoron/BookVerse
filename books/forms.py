from django import forms
from books.models import Book, Author, Category

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'image']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']