from django.contrib.auth.models import User
from django.http import JsonResponse

from book.models import Category


def is_username_available(request, username):
    try:
        user = User.objects.get(username=username)
        return JsonResponse({'available': False})
    except User.DoesNotExist:
        return JsonResponse({'available': True})


def add_interest(request, interest):
    try:
        category = Category.objects.get(name=interest)
        request.user.profile.interests.add(category)
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def del_interest(request, interest):
    try:
        category = Category.objects.get(name=interest)
        request.user.profile.interests.remove(category)
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)