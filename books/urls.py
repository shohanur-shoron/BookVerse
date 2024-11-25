from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('getAuthors/', api.get_authors, name='get_authors'),
    path('getCategory/', api.get_category, name='get_category'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/update/', views.AuthorUpdateView, name='AuthorUpdateView'),
    path('category/create/', views.CategoryCreate.as_view(), name='category-create'),
    path('category/all/', views.category_page, name='category_page'),
    path('add/', views.create_book, name="create_book"),
    path('add_to_favorites/<str:id>/', views.add_to_favorites, name="add_to_favorites"),
    path('remove_from_favorites/<str:id>/', views.remove_from_favorites, name="remove_from_favorites"),
    path('favorites', views.favorites_books, name="favorites_books"),
]