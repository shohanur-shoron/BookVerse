from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from books.models import Category, Book, Author

def get_site_url():
    site = Site.objects.get_current()
    protocol = 'https://'
    return f'{protocol}{site.domain}'


def add_interest(request, interest):
    try:
        category = Category.objects.get(name=interest)
        request.user.profile.interests.add(category)  # Note: it's 'interests' not 'interest'
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def del_interest(request, interest):
    try:
        category = Category.objects.get(name=interest)
        request.user.profile.interests.remove(category)  # Note: it's 'interests' not 'interest'
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def is_username_available(request, username):

    try:
        user = User.objects.get(username=username)
        return JsonResponse({'available': False})
    except User.DoesNotExist:
        return JsonResponse({'available': True})


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
