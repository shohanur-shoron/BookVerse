from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('getAuthors/', api.get_authors, name='get_authors'),
    path('getCategory/', api.get_category, name='get_category'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdateView.as_view(), name='author-update'),
]