from django.urls import path, include

from . import views, views2

urlpatterns = [
    path('', views.mainHomePage, name='mainHomePage'),
    path('category/all/', views.category_page, name='category_page'),
    path('books/fine-yours/', views.book_ai, name='book_ai'),
    path('user/peofile', views.user_profile, name='user_profile'),
    path('congrats/', views.congratulations_page, name='congratulations_page'),
    path('events/', views.events, name='events'),
    path('search-suggestions', views.search_items, name='search_items'),
    path('category/<int:id>', views.specific_category, name='specific_category'),
    path('reviewer/progile/<int:id>', views.reviewer_profile, name='reviewer_profile'),
    path('favourites/', views.favoriteBooksPage, name='favoriteBooksPage'),
    path('discover/', views.discoverBooksPage, name='discoverBooksPage'),
    path('your-comments/', views2.your_comments, name='your_comments'),
    path('your-favourites/', views2.your_favorites, name='your_favorites'),
    path('recently-seen/', views2.recently_seen, name='recently_seen'),
    path('liked/', views2.liked_books, name='liked_books'),
    path('currently-reading/', views2.currently_reading_books, name='currently_reading_books'),
    path('api/update-progress/', views2.update_reading_progress_api, name='update_reading_progress_api'),
    path('read-in-future/', views2.want_to_read_books, name='want_to_read_books'),
    path('move_to_Currently_Reading_Books/<int:id>', views2.move_to_Currently_Reading_Books, name='move_to_Currently_Reading_Books'),
    path('finished_reading/', views2.finish_reading_books, name='finish_reading_books'),
    path('talkto/AI/<int:id>', views.specific_book_ai, name='specific_book_ai'),
    path('fine-book', views.find_book_ai, name='find_book_ai'),
]