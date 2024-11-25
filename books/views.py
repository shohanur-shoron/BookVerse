from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Author, Book, Category, Favorite
from .forms import AuthorForm, CategoryForm
from django.contrib import messages


def check_author(name):
    try:
        author = Author.objects.get(name=name)
        return True
    except Author.DoesNotExist:
        return False

class AuthorCreate(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('mainHomePage')
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        form.save()
        return super().form_valid(form)


class CategoryCreate(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('mainHomePage')



def AuthorUpdateView(request):
    if request.method == 'POST':
        image = request.FILES.get('imageUpload')
        name = request.POST.get('name')
        author = Author.objects.get(name=name)
        if image:
            author.image = image
        author.save()
        return redirect('mainHomePage')
    return render(request, 'forms/add_Author.html')



def create_book(request):
    global author
    if request.method == 'POST':

        if check_author(request.POST['authors']):
            author = Author.objects.get(name=request.POST['authors'])
        else:
            author = Author.objects.create(name=request.POST['authors'])
            author.save()
            author.added_by = request.user
            author.save()
        try:
            new_book = Book(
                name=request.POST.get('bookName'),
                description=request.POST.get('description'),
                category=Category.objects.get(name=request.POST.get('category')),
                price=request.POST.get('price'),
                authors=author,
                rating=request.POST.get('rating'),
                suggestions=request.POST.get('suggestions'),
                link=request.POST.get('link'),
                pages=request.POST.get('pages', 0),
                language=request.POST.get('language'),
                chapters=request.POST.get('chapters', 0),
                favorites_chapters=request.POST.get('favoritesChapters'),
                favorites_quotes=request.POST.get('favoritesQuotes'),
                series=request.POST.get('series'),
                best_character=request.POST.get('bestCharacter'),
                awards=request.POST.get('awards'),
                format=request.POST.get('format')
            )
            new_book.save()

            # Handle file upload
            if request.FILES['bookCover']:
                new_book.image = request.FILES['bookCover']
                new_book.save()

            messages.success(request, 'Book created successfully!')


            return redirect('mainHomePage')

        except Exception as e:
            messages.error(request, f'Error creating book: {str(e)}')
            # Return to form with entered data
            return render(request, 'forms/book_form.html', {'form_data': request.POST})

    # If GET request, show empty form
    return render(request, 'forms/book_form.html')


def category_page(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, "homePages/category.html", context)


def add_to_favorites(request, id):
    book = get_object_or_404(Book, pk=id)
    user = request.user
    favorite = Favorite.objects.create(user=user, book=book)
    favorite.save()
    return JsonResponse("Favorites Added with id: {id}".format(id=favorite.id), safe=False)

def remove_from_favorites(request, id):
    book = get_object_or_404(Book, pk=id)
    user = request.user
    favorites = Favorite.objects.filter(user=user, book=book)

    if favorites.exists():
        favorites.delete()
        return JsonResponse("Favorites Removed Successfully", safe=False)
    return JsonResponse("Favorites Not Found", safe=False)


def favorites_books(request):
    favorite_books = Book.objects.filter(favorite__user=request.user)
    context = {
        'books': favorite_books,
        'favorite_books': favorite_books,
    }
    return render(request, "homePages/mainHomePage.html", context)