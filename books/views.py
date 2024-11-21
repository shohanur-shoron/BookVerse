from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Author, Book, Category
from .forms import AuthorForm
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
    success_url = reverse_lazy('index')
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class AuthorUpdateView(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'forms/generic_form.html'
    success_url = reverse_lazy('author-list')



def create_book(request):
    global redirectToAuthor
    global author
    if request.method == 'POST':

        if check_author(request.POST['author_name']):
            author = Author.objects.get(name=request.POST['author_name'])
        else:
            author = Author.objects.create(name=request.POST['author_name'])
            author.save()
            redirectToAuthor = True
        try:
            new_book = Book(
                name=request.POST.get('bookName'),
                description=request.POST.get('description'),
                category=request.POST.get('category'),
                price=request.POST.get('price'),
                authors=author,
                rating=request.POST.get('rating'),
                suggestions=request.POST.get('suggestions'),
                link=request.POST.get('link'),
                pages=request.POST.get('pages'),
                language=request.POST.get('language'),
                chapters=request.POST.get('chapters'),
                favoritesChapters=request.POST.get('favoritesChapters'),
                favoritesQuotes=request.POST.get('favoritesQuotes'),
                series=request.POST.get('series'),
                bestCharacter=request.POST.get('bestCharacter'),
                awards=request.POST.get('awards'),
                format=request.POST.get('format')
            )

            # Handle file upload
            if request.FILES.get('bookCover'):
                new_book.bookCover = request.FILES['bookCover']


            new_book.save()
            messages.success(request, 'Book created successfully!')


            if redirectToAuthor:
                return render('forms/add_Author.html', {'author': author})
            else:
                return redirect('index')

        except Exception as e:
            messages.error(request, f'Error creating book: {str(e)}')
            # Return to form with entered data
            return render(request, 'forms/book_form.html', {'form_data': request.POST})

    # If GET request, show empty form
    return render(request, 'forms/book_form.html')