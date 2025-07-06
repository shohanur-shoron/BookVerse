# library/forms.py
from django import forms
from .models import Book, Author, Category, Event

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active'] # Exclude added_by (set in view)
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'image'] # Exclude followers, addedBy (set in view/handled separately)

class BookForm(forms.ModelForm):
    # Make authors selection potentially easier if you have many
    authors = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}) # Example using a specific widget class
    )

    class Meta:
        model = Book
        # Exclude fields set automatically or handled differently
        exclude = [
            'publisher', 'total_views', 'rating', 'link_clicked',
            'likes_counter', 'likes', 'published_time', 'addedBy' # Assuming addedBy isn't a field in Book model
         ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'suggestions': forms.Textarea(attrs={'rows': 3}),
            'favorites_quotes': forms.Textarea(attrs={'rows': 3}),
            'awards': forms.Textarea(attrs={'rows': 2}),
            # Use Select widgets for choices and foreign keys if not using default
            'category': forms.Select(attrs={'class': 'form-select'}),
            'authors': forms.Select(attrs={'class': 'form-select'}),
            'format': forms.Select(attrs={'class': 'form-select'}),
        }
        # Add help text if desired
        help_texts = {
            'price': 'Enter price in your local currency value (e.g., 15).',
            'pages': 'e.g., 350 pages',
        }

class EventForm(forms.ModelForm):
     class Meta:
        model = Event
        fields = ['name', 'description', 'image', 'ongoing']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }