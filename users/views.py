from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse


from mainpages.views import mainHomePage
from .models import *
from .utills import *
from book.models import Category, Book



def create_account(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        username = generate_unique_username(firstname, lastname)

        # Check if passwords match
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('create_account')

        # Check if phone number already exists
        if Profile.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered!')
            return redirect('create_account')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
            )

            user.save()

            user.profile.phone = phone
            user.profile.gender = gender
            user.profile.is_user = True
            user.profile.is_reviewer = False
            user.profile.save()

            login(request, user)
            return redirect('update_username')

        except Exception as e:
            if 'user' in locals():
                user.delete()
            messages.error(request, 'An error occurred while creating your account.')
            return redirect('create_account')

    return render(request, 'account/signup.html')

def username(request):
    return render(request, "account/updateUsername.html")

def update_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username == '':
            messages.error(request, 'Username cannot be empty!')
            return redirect('update_username')

        if username == request.user.username:
            return redirect('upload_image')

        try:
            user = User.objects.get(username=username)
            messages.error(request, 'Username already registered! Pick another one.')
            return redirect('update_username')
        except:
            request.user.username = username
            request.user.save()
            return redirect('upload_image')

    return render(request, 'account/updateUsername.html')


def upload_image(request):
    if request.method == 'POST':
        if 'imageUpload' in request.FILES:
            image = request.FILES['imageUpload']
            if image:
                user = User.objects.get(username=request.user.username)
                user.profile.image = image
                user.profile.save()
                return redirect('add_your_interest')
            else:
                messages.error(request, "Invalid image file")

    return render(request, 'account/updateProfileImage.html')


def add_your_interest(request):
    interests = Category.objects.all()
    user_interests = list(request.user.profile.interests.values_list('name', flat=True))

    context = {
        'interests': interests,
        'user_interests': user_interests
    }
    return render(request, 'account/updateInterest.html', context)


def login_user(request):
    if request.method == 'POST':
        login_identifier = request.POST.get('username')
        password = request.POST.get('password')

        try:
            if is_phone_number(login_identifier):
                # It's a phone number, try to get the user by phone
                try:
                    user = Profile.objects.get(phone=login_identifier).user
                    username = user.username
                except Profile.DoesNotExist:
                    messages.error(request, 'User with this phone number not found')
                    return redirect('login_user')

            else:
                username = login_identifier

            # Attempt to authenticate the user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(mainHomePage)
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login_user')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('login_user')

    return render(request, "account/login.html")




def logout_user(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect(mainHomePage)

def delete_user(request):
    user = request.user
    user.delete()
    logout(request)
    return redirect(mainHomePage)



def update_account(request):
    if request.method == 'POST':
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        email = request.POST.get('phone')
        phone = request.POST.get('email')
        gender = request.POST.get('gender')

        user = request.user

        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.save()

        user.profile.phone = phone
        user.profile.gender = gender
        user.profile.save()

        return redirect("update_account")

    return render(request, "account/updateAccount/personalDetails.html")

def change_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username == '':
            messages.error(request, 'Username cannot be empty!')
            return redirect('change_username')
        if username == request.user.username:
            messages.error(request, 'Username already registered!')
            return redirect('change_username')
        request.user.username = username
        request.user.save()
        return redirect("change_username")
    return render(request, "account/updateAccount/username.html")

def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('oldPass')
        new_password = request.POST.get('newPass')

        user = authenticate(username=request.user.username, password=old_password)

        if user is not None:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            return redirect('logout_user')

    return render(request, "account/updateAccount/changePassword.html")

def change_image(request):
    if request.method == 'POST':
        image = request.FILES['imageUpload']
        if image:
            request.user.profile.image = image
            request.user.profile.save()
            return redirect("change_image")

    return render(request, "account/updateAccount/changeImage.html")

def change_interest(request):
    interests = Category.objects.values_list('name', flat=True)
    user_interests = request.user.profile.interests.values_list('name', flat=True)

    context = {
        'interests': interests,
        'user_interests': list(user_interests)
    }

    return render(request, "account/updateAccount/changeInterest.html", context)


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



