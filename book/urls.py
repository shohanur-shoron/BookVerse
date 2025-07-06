from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.create_book, name='create_book'),
    path('add_to_favorites/<str:id>/', views.add_to_favorites, name="add_to_favorites"),
    path('remove_from_favorites/<str:id>/', views.remove_from_favorites, name="remove_from_favorites"),
    path('favorites', views.favorites_books, name="favorites_books"),
    path('getAuthors/', views.get_authors, name='get_authors'),
    path('getCategory/', views.get_category, name='get_category'),
    path('view/<int:pk>', views.book_detail_view, name='book_detail_view'),
    path('comment/', views.add_comment_view, name='add_comment_view'),
    path('like/', views.like_book_view, name='like_book_view'),
    path('addToFav/', views.toggle_favourite_view, name="toggle_favourite_view"),
    path('add_to_reading_list/', views.add_to_reading_list_view, name='add_to_reading_list'),
]