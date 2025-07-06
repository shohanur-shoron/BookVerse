import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from book.models import *
from django.contrib.auth.models import User

SIMILARITY_THRESHOLD = 60

from django.db.models import Q
from thefuzz import fuzz

def get_user_comments_details(request):
    if not request.user.is_authenticated:
        return []

    user_comments = Comment.objects.filter(user=request.user).select_related('book').order_by('-created_at')

    comments_data = []
    for comment in user_comments:
        book_cover_url = None
        if comment.book and comment.book.image:
             try:
                 book_cover_url = comment.book.image.url
             except ValueError:
                 book_cover_url = None

        comments_data.append({
            'book_id': comment.book.id,
            'book_title': comment.book.name,
            'comment_text': comment.text,
            'book_cover_url': book_cover_url,
            'rating': comment.rating,
            'comment_created_at': comment.created_at
        })

    return comments_data

def add_recently_viewed(user, book):
    if not user.is_authenticated:
        return

    obj, created = RecentlyViewedBook.objects.update_or_create(
        user=user,
        book=book,
        defaults={'timestamp': timezone.now()}
    )

    # Keep only the most recent 50 entries
    max_recent = 50
    qs = RecentlyViewedBook.objects.filter(user=user)
    if qs.count() > max_recent:
        # Get the primary keys of the oldest entries to delete
        ids_to_delete = qs.order_by('timestamp').values_list('id', flat=True)[:qs.count() - max_recent]
        # Delete the oldest entries
        RecentlyViewedBook.objects.filter(pk__in=list(ids_to_delete)).delete()

def get_to_read_books(request):
    """'Read in Future' - Books the user wants to read."""
    if not request.user.is_authenticated:
        return Book.objects.none()
    # Get IDs of books 'to_read'
    to_read_book_ids = ReadingStatus.objects.filter(
        user=request.user,
        status='to_read'
    ).values_list('book_id', flat=True)
    # Get the actual Book objects
    return Book.objects.filter(pk__in=to_read_book_ids)


def get_currently_reading_books(request):
    """'Finished Reading' - Books the user has marked as completed."""
    if not request.user.is_authenticated:
        return Book.objects.none()
    # Get IDs of completed books
    currently_book_ids = ReadingStatus.objects.filter(
        user=request.user,
        status='reading'
    ).values_list('book_id', flat=True)
    # Get the actual Book objects
    return Book.objects.filter(pk__in=currently_book_ids)

def get_finished_reading_books(request):
    """'Finished Reading' - Books the user has marked as completed."""
    if not request.user.is_authenticated:
        return Book.objects.none()
    # Get IDs of completed books
    completed_book_ids = ReadingStatus.objects.filter(
        user=request.user,
        status='completed'
    ).values_list('book_id', flat=True)
    # Get the actual Book objects
    return Book.objects.filter(pk__in=completed_book_ids)


def your_comments(request):
    context = {
        'comments_list': get_user_comments_details(request)
    }
    return render(request, 'sidePanel/yourComment.html', context)

def your_favorites(request):
    favorite_books = Book.objects.filter(favorite__user=request.user)
    context = {
        'books': favorite_books,
        'title_text': 'Your Favorites',
    }
    return render(request, 'sidePanel/your-favourite.html', context)

def recently_seen(request):
    limit = 50

    recent_views = RecentlyViewedBook.objects.filter(
        user=request.user
    ).select_related('book').order_by('-timestamp')[:limit]

    recently_seen_books = [view.book for view in recent_views]

    context = {
        'books': recently_seen_books,
        'title_text': 'Recently Viewed Books',
    }
    return render(request, 'sidePanel/your-favourite.html', context)


def liked_books(request):
    user_liked_books = Book.objects.filter(
        likes=request.user
    ).order_by('-published_time')
    context = {
        'books': user_liked_books,
        'title_text': 'Your Liked Books',
    }
    return render(request, 'sidePanel/your-favourite.html', context)


def currently_reading_books(request):
    reading_statuses = ReadingStatus.objects.filter(
        user=request.user,
        status='reading'
    )
    context = {
        'reading_statuses': reading_statuses,
        'title_text': 'Current Reading Books',
    }
    return render(request, 'sidePanel/current_reading.html', context)


def update_reading_progress_api(request):
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        current_page_str = data.get('current_page')

        if book_id is None or current_page_str is None:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        try:
            current_page = int(current_page_str)
            if current_page < 0:
                raise ValueError("Page number cannot be negative.")
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid page number.'}, status=400)

        reading_status = get_object_or_404(
            ReadingStatus,
            user=request.user,
            book_id=book_id,
            status='reading'
        )

        book_total_pages = reading_status.book.pages
        try:
            total_pages = int(book_total_pages) if book_total_pages else 0
            if total_pages <= 0:
                 pass
        except (ValueError, TypeError):
            total_pages = 0

        if total_pages > 0 and current_page > total_pages:
            current_page = total_pages

        reading_status.current_page = current_page
        new_status = 'reading'

        if total_pages > 0 and current_page >= total_pages:
            reading_status.status = 'completed'
            new_status = 'completed'

        reading_status.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Progress updated.',
            'book_id': book_id,
            'current_page': reading_status.current_page,
            'total_pages': total_pages,
            'reading_status': new_status
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
    except ReadingStatus.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Reading status not found or not \'reading\'.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)


def search_books_sqlite_fuzzy(query):
    if not query or not query.strip():
        return []

    query = query.strip()
    initial_lookups = (
        Q(name__icontains=query) |
        Q(authors__name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(series__icontains=query)

    )
    candidate_books = Book.objects.filter(initial_lookups).distinct().select_related('authors', 'category')

    results_with_scores = []
    for book in candidate_books:
        name_score = fuzz.token_set_ratio(query, book.name)
        author_name = book.authors.name if book.authors else ""
        author_score = fuzz.token_set_ratio(query, author_name)

        highest_score = max(name_score, author_score * 1.1) # Slightly boost author score relevance if desired

        if highest_score >= SIMILARITY_THRESHOLD:
            results_with_scores.append({'book': book, 'score': highest_score})

    sorted_results = sorted(results_with_scores, key=lambda item: item['score'], reverse=True)
    final_book_list = [item['book'] for item in sorted_results]
    return final_book_list


def want_to_read_books(request):
    books = get_to_read_books(request)

    context = {
        'books': books,
        'title_text': 'Future Read Books',
    }
    return render(request, 'sidePanel/future_read.html', context)


def move_to_Currently_Reading_Books(request, id):
    book = get_object_or_404(Book, pk=id)
    reading_status = ReadingStatus.objects.get(user=request.user, book=book)

    reading_status.status = 'reading'
    reading_status.save()

    return redirect('want_to_read_books')


def finish_reading_books(request):
    books = get_finished_reading_books(request)

    context = {
        'books': books,
        'title_text': 'Finished Reading Books',
    }

    return render(request, 'sidePanel/your-favourite.html', context)

