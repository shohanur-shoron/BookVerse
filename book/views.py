import json

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Author, Book, Category, Favorite, Comment, ReadingStatus
from .forms import AuthorForm, CategoryForm
from django.contrib import messages
from .models import Author, Category
from django.http import JsonResponse
from mainpages.views2 import add_recently_viewed
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def check_author(name):
    try:
        author = Author.objects.get(name=name)
        return True
    except Author.DoesNotExist:
        return False

def check_catecory(name):
    try:
        category = Category.objects.get(name=name)
        return True
    except Category.DoesNotExist:
        return False


def create_book(request):
    global author
    global category
    if request.method == 'POST':
        if check_author(request.POST['authors']):
            author = Author.objects.get(name=request.POST['authors'])
        else:
            author = Author.objects.create(name=request.POST['authors'])
            author.save()
            author.added_by = request.user
            author.save()

        if check_catecory(request.POST.get('category')):
            category = Category.objects.get(name=request.POST.get('category'))
        else:
            category = Category.objects.create(name=request.POST['authors'])
            category.save()
            category.added_by = request.user
            category.save()
        try:
            new_book = Book(
                name=request.POST.get('bookName'),
                description=request.POST.get('description'),
                category=category,
                price=request.POST.get('price'),
                authors=author,
                publisher=request.user,
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

            # Handle file upload only if a file is present
            if 'bookCover' in request.FILES and request.FILES['bookCover']:
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



def add_to_favorites(request, id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, pk=id)
        user = request.user
        favorite = Favorite.objects.create(user=user, book=book)
        favorite.save()
        return JsonResponse("Favorites Added with id: {id}".format(id=favorite.id), safe=False)
    else:
        return redirect('login_user')

def remove_from_favorites(request, id):
    book = get_object_or_404(Book, pk=id)
    user = request.user
    favorites = Favorite.objects.filter(user=user, book=book)

    if favorites.exists():
        favorites.delete()
        return JsonResponse("Favorites Removed Successfully", safe=False)
    return JsonResponse("Favorites Not Found", safe=False)


def favorites_books(request):
    if request.user.is_authenticated:
        favorite_books = Book.objects.filter(favorite__user=request.user)
        context = {
            'books': favorite_books,
            'favorite_books': favorite_books,
        }
        return render(request, "homePage/home.html", context)
    else:
        return redirect('login_user')



def get_authors(request):
    author_names = list(Author.objects.values_list('name', flat=True))
    return JsonResponse(author_names, safe=False)

def get_category(request):
    category_names = list(Category.objects.values_list('name', flat=True))
    return JsonResponse(category_names, safe=False)


def get_single_author(text):
    if ',' in text:
        text = text.split(',')
        return text[0]
    return text

def book_detail_view(request, pk):
    global favorite_books, reading_list
    book = get_object_or_404(Book, pk=pk)
    add_recently_viewed(request.user, book)
    comments = Comment.objects.filter(book=book)
    if request.user.is_authenticated:
        favorite_books = Book.objects.filter(favorite__user=request.user)
        reading_list = Book.objects.filter(readingstatus__user=request.user)
    book.total_views += 1
    book.save(update_fields=['total_views'])
    total_comments = comments.count()
    total_ratting = 0
    for comment in comments:
        total_ratting += comment.rating

    if total_ratting != 0:
        avg = total_ratting/total_comments
    else:
        avg = 0

    sentiment_score = 0
    for comment in comments:
        sentiment_score += comment.textSentimentScore


    #temp code

    # with open('data.json', 'r') as file:
    #     json_books = json.load(file)
    #
    # for json_book in json_books:
    #     author_name_raw = json_book.get('authors')
    #     author_name = get_single_author(author_name_raw)
    #     author_obj, created_auth = Author.objects.get_or_create(name=author_name)
    #
    #     new_book = Book.objects.create(
    #         name=json_book.get('name'),
    #         description=json_book.get('description'),
    #         category=Category.objects.get(name=json_book.get('category')),
    #         price=json_book.get('price')*120,
    #         authors=author_obj,
    #         publisher=request.user,
    #         rating=json_book.get('rating'),
    #         suggestions='People who like to read books.',
    #         pages=json_book.get('pages'),
    #         language=json_book.get('language'),
    #         chapters=json_book.get('chapters') if json_book.get('chapters') is not None else 30,
    #         favorites_chapters=json_book.get('favorites_chapters') if json_book.get('favorites_chapters') is not None else 15,
    #         favorites_quotes=json_book.get('favorites_quotes'),
    #         series=json_book.get('series'),
    #         best_character=json_book.get('best_character'),
    #         awards=json_book.get('awards'),
    #         format=json_book.get('format'),
    #     )
    #     new_book.save()




    if sentiment_score != 0:
        sentiment = get_sentiment(sentiment_score/len(comments)) #positive or negetive
    else: sentiment = 'N/A'

    context = {
        'book': book,
        'comments': comments,
        'average': f'{avg:.2f}' if avg != 0 else '0',
        'favorite_books': favorite_books if request.user.is_authenticated else [],
        'reading_list': reading_list if request.user.is_authenticated else [],
        'sentiment_score': sentiment_score,
        'sentiment' : sentiment,
    }

    return render(request, 'homePage/card-detailed-view.html', context)


def analyze_comment_sentiment_vader(text_content):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text_content)
    compound_score = vs['compound']

    if compound_score >= 0.5:
         sentiment_category = "Overwhelmingly Positive"
    elif compound_score > 0.05:
         sentiment_category = "Positive"
    elif compound_score <= -0.5:
         sentiment_category = "Overwhelmingly Negative"
    elif compound_score < -0.05:
         sentiment_category = "Negative"
    else:
         sentiment_category = "Neutral"

    return compound_score, sentiment_category

def get_sentiment(compound_score):
    if compound_score >= 0.5:
         sentiment_category = "Overwhelmingly Positive"
    elif compound_score > 0.05:
         sentiment_category = "Positive"
    elif compound_score <= -0.5:
         sentiment_category = "Overwhelmingly Negative"
    elif compound_score < -0.05:
         sentiment_category = "Negative"
    else:
         sentiment_category = "Neutral"
    return sentiment_category


def add_comment_view(request):
    """Handles submission of a new comment."""
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        comment_text = data.get('comment_text', '').strip()
        rating = data.get('rating')

        if not all([book_id, comment_text, rating is not None]): # Check rating exists
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5.")
        except (ValueError, TypeError):
             return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)

        book = get_object_or_404(Book, pk=book_id)

        compound_score, sentiment_category = analyze_comment_sentiment_vader(comment_text)

        Comment.objects.create(
            book=book,
            user=request.user,
            text=comment_text,
            textSentimentScore=compound_score,
            sentimentCategory=sentiment_category,
            rating=rating
        )
        # Optional: Update book's average rating here if needed

        return JsonResponse({'status': 'success', 'message': 'Comment added successfully!'}, status=201)

    except json.JSONDecodeError:
         return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Book.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        print(f"Error in add_comment_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred'}, status=500)

# --- Like View (Uses 'likes' M2M field) ---

def like_book_view(request):
    """Handles liking a book. Adds user to 'likes' M2M."""
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({'status': 'error', 'message': 'Missing book_id'}, status=400)

        book = get_object_or_404(Book, pk=book_id)
        user = request.user

        # Using the M2M field 'likes'
        # add() handles duplicates gracefully
        book.likes.add(user)

        # Get the updated count from the M2M relationship
        new_count = book.likes.count()

        # Update the separate counter field if you still need it (redundant?)
        book.likes_counter = new_count
        book.save(update_fields=['likes_counter'])

        return JsonResponse({'status': 'success', 'new_count': new_count})

    except json.JSONDecodeError:
         return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Book.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        print(f"Error in like_book_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred'}, status=500)


# --- Favourite Toggle View (Using 'likes' M2M field for favorites) ---
# IMPORTANT: This assumes 'likes' is used for *both* likes and favorites.
# It's better practice to have a separate field like 'favorited_by'.
# If you add `favorited_by = models.ManyToManyField(...)`, change the logic below.

def toggle_favourite_view(request):
    """Adds or removes a book from the user's favourites using the Favorite model."""
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({'status': 'error', 'message': 'Missing book_id'}, status=400)

        book = get_object_or_404(Book, pk=book_id)
        user = request.user
        is_favourite_after_toggle = False # State *after* the action

        # Check if a Favorite object exists for this user and book
        favorite_instance, created = Favorite.objects.get_or_create(
            user=user,
            book=book
        )

        if created:
            # The object was just created, meaning it wasn't a favorite before.
            # It is now favourited.
            is_favourite_after_toggle = True
            message = "Book added to favorites."
        else:
            # The object already existed (get_or_create returned existing instance).
            # This means it *was* a favorite, so we delete it.
            favorite_instance.delete()
            is_favourite_after_toggle = False
            message = "Book removed from favorites."

        # Return the final state for the JS to update UI
        return JsonResponse({
            'status': 'success',
            'message': message, # Optional message
            'is_favourite': is_favourite_after_toggle
        })

    except json.JSONDecodeError:
         return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Book.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        print(f"Error in toggle_favourite_view: {e}") # Replace with proper logging
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred'}, status=500)


def add_to_reading_list_view(request):
    """Adds or updates a book's status in the user's reading list to 'to_read'."""
    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({'status': 'error', 'message': 'Missing book_id'}, status=400)

        book = get_object_or_404(Book, pk=book_id)
        user = request.user

        # Use update_or_create to handle existing entries
        # This will set the status to 'to_read' regardless of previous status
        # when this specific action is triggered.
        # It also prevents duplicate entries for the same user/book.
        reading_status_obj, created = ReadingStatus.objects.update_or_create(
            user=user,
            book=book,
            defaults={'status': 'to_read'}
        )

        message = "Book added to reading list (status: To Read)." if created else "Book status updated to 'To Read' in your list."

        return JsonResponse({
            'status': 'success',
            'message': message,
            # Optionally return the status if JS needs it
            'reading_status': reading_status_obj.status
        })

    except json.JSONDecodeError:
         return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Book.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Book not found'}, status=404)
    except Exception as e:
        print(f"Error in add_to_reading_list_view: {e}") # Replace with proper logging
        return JsonResponse({'status': 'error', 'message': 'An internal server error occurred'}, status=500)