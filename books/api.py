from .models import Author, Category
from django.http import JsonResponse

def get_authors(request):
    author_names = list(Author.objects.values_list('name', flat=True))
    return JsonResponse(author_names, safe=False)

def get_category(request):
    category_names = list(Category.objects.values_list('name', flat=True))
    return JsonResponse(category_names, safe=False)