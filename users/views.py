from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import random
import string
import re

from BookVerse.views import mainHomePage
from users.models import Profile
from books.models import Category


def generate_unique_username(first_name='shoron', last_name='rahman'):
    # Create initial username
    username = f"{first_name.lower()}{last_name.lower()}"
    # Remove any spaces
    username = username.replace(" ", "")
    # Check if username exists
    if not User.objects.filter(username=username).exists():
        return username
    # If username exists, add random characters
    while True:
        # Generate 5 random characters
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        # Create new username with random string
        new_username = f"{username}{random_string}"
        # Check if new username exists
        if not User.objects.filter(username=new_username).exists():
            return new_username


def is_phone_number(input_string):
    # Remove any whitespace from the input
    input_string = input_string.strip()

    # Define the regex patterns for phone numbers
    pattern_01 = r'^01\d{9}$'  # Matches 11 digits starting with 01
    pattern_880 = r'^\+880\d{10}$'  # Matches +880 followed by 10 digits

    # Check if the input matches either phone number pattern
    if re.match(pattern_01, input_string) or re.match(pattern_880, input_string):
        return True

    # If it doesn't match the phone patterns, check if it's a valid username
    # is considered valid if it contains at least one letter
    if re.search(r'[a-zA-Z]', input_string):
        return False

    # If it contains only numbers but doesn't match the phone patterns, it's not a valid phone number
    return False


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
                # It's a username
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

    return render(request, "signupAndLogin/login.html")


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)

    return redirect(mainHomePage)


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

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('create_account')

        try:
            # Create User instance
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
            return render(request, "signupAndLogin/updateUsername.html", {'username': username})

        except Exception as e:
            # If any error occurs, delete the user if it was created
            if 'user' in locals():
                user.delete()
            messages.error(request, 'An error occurred while creating your account.')
            return redirect('create_account')

    return render(request, 'signupAndLogin/signup.html')

def update_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username == '':
            messages.error(request, 'Username cannot be empty!')
            return redirect('update_username')

        if username == request.user.username:
            return render(request, 'signupAndLogin/updateProfileImage.html')

        try:
            user = User.objects.get(username=username)
            messages.error(request, 'Username already registered! Pick another one.')
            return redirect('update_username')
        except:
            request.user.username = username
            request.user.save()
            return render(request, 'signupAndLogin/updateProfileImage.html')

    return render(request, 'signupAndLogin/updateUsername.html')


def upload_image(request):
    if request.method == 'POST':
        if 'imageUpload' in request.FILES:
            image = request.FILES['imageUpload']
            if image:
                try:
                    request.user.profile.image = image
                    request.user.profile.save()
                    return redirect(add_interest)
                except Exception as e:
                    messages.error(request, "Error uploading image")
            else:
                messages.error(request, "Invalid image file")

    return render(request, 'signupAndLogin/updateProfileImage.html')


def add_interest(request):
    interests = Category.objects.values_list('name', flat=True)
    user_interests = request.user.profile.interests.values_list('name', flat=True)

    context = {
        'interests': interests,
        'user_interests': list(user_interests)
    }

    return render(request, 'signupAndLogin/updateInterest.html', context)








