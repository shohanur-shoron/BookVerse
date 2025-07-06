from django.http import JsonResponse
from django.shortcuts import render
from book.models import *
from users.models import *
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .views2 import search_books_sqlite_fuzzy


def get_interested_books(request):
    """
    Returns a QuerySet of books whose category matches the interests
    of the logged-in user associated with the request.
    Returns an empty QuerySet if the user is not authenticated,
    has no profile, or has no interests selected.
    """
    if not request.user.is_authenticated:
        return Book.objects.none()

    try:
        profile = request.user.profile
        interested_categories = profile.interests.all()

        if not interested_categories.exists():
            return Book.objects.none() # No interests selected

        # Filter books where the book's category is in the user's interested categories
        return Book.objects.filter(category__in=interested_categories).distinct()

    except (Profile.DoesNotExist, AttributeError):
        # Profile doesn't exist for the user, or reverse relation isn't 'profile'
        return Book.objects.none()


def get_not_interested_books(request):
    """
    Returns a QuerySet of books whose category does NOT match the interests
    of the logged-in user associated with the request.
    Returns all books if the user is not authenticated, has no profile,
    or has no specific interests selected (as no categories can be excluded).
    """
    if not request.user.is_authenticated:
        return Book.objects.all() # Anonymous user isn't interested/not-interested based on profile

    try:
        profile = request.user.profile
        interested_categories = profile.interests.all()

        if not interested_categories.exists():
            # If the user has no specific interests, we can't exclude anything based on them.
            # Therefore, all books are potentially "not interested" based on profile data.
            return Book.objects.all()

        # Exclude books where the book's category is in the user's interested categories
        return Book.objects.exclude(category__in=interested_categories).distinct()

    except (Profile.DoesNotExist, AttributeError):
        # Profile doesn't exist, so we can't determine specific interests to exclude.
        # Return all books.
        return Book.objects.all()

def mainHomePage(request):
    if request.user.is_authenticated:
        global books
        if request.method == 'POST':
            search_text = request.POST['searchText']
            books = search_books_sqlite_fuzzy(search_text)
        else:
            books = get_interested_books(request)
        favorite_books = []
        if request.user.is_authenticated:
            favorite_books = Book.objects.filter(favorite__user=request.user)
        contex = {
            'books': books,
            'favorite_books': favorite_books if request.user.is_authenticated else None,
        }
        return render(request, 'homePage/home.html', contex)
    else:
        contex = {
            'books': Book.objects.all()
        }
        return render(request, 'homePage/home.html', contex)


def favoriteBooksPage(request):
    favorite_books = []
    if request.user.is_authenticated:
        favorite_books = Book.objects.filter(favorite__user=request.user)
    contex = {
        'books': favorite_books if request.user.is_authenticated else None,
        'favorite_books': favorite_books if request.user.is_authenticated else None,
    }
    return render(request, 'homePage/home.html', contex)


def discoverBooksPage(request):
    books = get_not_interested_books(request)
    favorite_books = []
    if request.user.is_authenticated:
        favorite_books = Book.objects.filter(favorite__user=request.user)
    contex = {
        'books': books,
        'favorite_books': favorite_books if request.user.is_authenticated else None,
    }
    return render(request, 'homePage/home.html', contex)

def specific_category(request, id):
    # Get the category object to pass to the template
    category = get_object_or_404(Category, id=id)

    # Get all books for this category
    books = Book.objects.filter(category=category)

    context = {
        'books': books,
    }

    return render(request, 'homePage/home.html', context)

def category_page(request):
    categories = Category.objects.all()


    context = {'categories': categories}
    return render(request, "homePage/categorys.html", context)


def book_ai(request):
    if request.user.is_authenticated:
        return render(request, 'homePage/gemini.html')
    else:
        return render(request, 'homePage/authNeed.html')

def find_book_ai(request):
    if request.user.is_authenticated:
        return render(request, 'homePage/gemeni-image.html')
    else:
        return render(request, 'homePage/authNeed.html')

def specific_book_ai(request, id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, id=id)
        prompt = f'Tell me more about {book.name} written by {book.authors.name}'

        context = {
            'book': book,
            'prompt': prompt,
        }
        return render(request, 'homePage/gemini_specific_book.html', context)
    else:
        return render(request, 'homePage/authNeed.html')


def user_profile(request):
    """
    Displays the profile page for a given username.

    Fetches the user, their profile, interests, favorites, reading lists,
    and followed authors to pass to the template.
    """
    # 1. Get the User object for the requested username
    #    - Returns a 404 error if the user does not exist.
    profile_user = request.user

    # 2. Get the associated Profile object
    #    - Uses prefetch_related to efficiently load the 'interests' ManyToMany field,
    #      avoiding extra database queries when accessing profile.interests.all in the template.
    try:
        profile = Profile.objects.prefetch_related('interests').get(user=profile_user)
    except Profile.DoesNotExist:

        profile = None

    favorite_books = Favorite.objects.filter(user=profile_user)\
                                     .select_related('book')\
                                     .order_by('-timestamp')[:10]

    reading_statuses = ReadingStatus.objects.filter(user=profile_user)\
                                            .select_related('book')\
                                            .order_by('-last_updated')

    books_to_read = reading_statuses.filter(status='to_read')[:10]
    books_reading = reading_statuses.filter(status='reading')[:10]
    books_completed = reading_statuses.filter(status='completed')[:10]


    followed_authors = Author.objects.filter(followers=profile_user)[:10]

    context = {
        'profile_user': profile_user, # The User object whose profile is being viewed
        'profile': profile,           # The associated Profile object (or None)
        'favorite_books': favorite_books, # QuerySet of Favorite objects
        'books_to_read': books_to_read,   # QuerySet of ReadingStatus objects
        'books_reading': books_reading, # QuerySet of ReadingStatus objects
        'books_completed': books_completed,# QuerySet of ReadingStatus objects
        'followed_authors': followed_authors, # QuerySet of Author objects
    }

    # 7. Render the template with the context data
    return render(request, 'homePage/userProfile.html', context)

def congratulations_page(request):
    request.user.profile.is_reviewer = True
    request.user.profile.save()
    return render(request, 'homePage/congratulations.html')


def events(request):
    events = Event.objects.filter(is_valid=True)

    context = {
        'events': events
    }

    return render(request, 'homePage/event.html', context)


def search_items(request):
    # Get all book instances
    books = Book.objects.all()
    categories = Category.objects.all()
    authors = Author.objects.all()

    # Prepare the data as a flat list
    data = []
    for book in books:
        data.extend([book.name])

    for categorie in categories:
        data.extend([categorie.name])

    for author in authors:
        data.extend([author.name])

    # Return the data as JSON
    return JsonResponse(data, safe=False)


def reviewer_profile(request, id):

    profile_user = User.objects.get(id=id)

    try:
        profile = Profile.objects.prefetch_related('interests').get(user=profile_user)
    except Profile.DoesNotExist:

        profile = None

    favorite_books = Favorite.objects.filter(user=profile_user)\
                                     .select_related('book')\
                                     .order_by('-timestamp')[:10]

    reading_statuses = ReadingStatus.objects.filter(user=profile_user)\
                                            .select_related('book')\
                                            .order_by('-last_updated')

    books_to_read = reading_statuses.filter(status='to_read')[:10]
    books_reading = reading_statuses.filter(status='reading')[:10]
    books_completed = reading_statuses.filter(status='completed')[:10]


    followed_authors = Author.objects.filter(followers=profile_user)[:10]

    context = {
        'profile_user': profile_user, # The User object whose profile is being viewed
        'profile': profile,           # The associated Profile object (or None)
        'favorite_books': favorite_books, # QuerySet of Favorite objects
        'books_to_read': books_to_read,   # QuerySet of ReadingStatus objects
        'books_reading': books_reading, # QuerySet of ReadingStatus objects
        'books_completed': books_completed,# QuerySet of ReadingStatus objects
        'followed_authors': followed_authors, # QuerySet of Author objects
    }

    return render(request, 'homePage/userProfile.html', context)