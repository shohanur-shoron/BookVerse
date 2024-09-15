from django.contrib.auth.models import User
from django.http import JsonResponse

from books.models import Category


def add_interest(request, interest):
    category = Category.objects.get(name=interest)
    request.user.profile.interest.add(category)


def del_interest(request, interest):
    try:
        category = Category.objects.get(name=interest)
        request.user.profile.interest.remove(category)
    except:
        return JsonResponse({'error': 'Category not found'}, status=404)


def is_username_available(request, username):
    try:
        user = User.objects.get(username=username)
        return JsonResponse({'available': False})
    except User.DoesNotExist:
        return JsonResponse({'available': True})

# def add_profile_image(request, username):
#     if request.method == 'POST':
#         image = request.FILES['image']
#         if image:
#             user = User.objects.get(username=username)
#             user.profile.image = image
