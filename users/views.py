from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import random
import string
import re

from users.models import Profile


def generate_unique_username(first_name, last_name):
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
        login_identifier = request.POST.get('login_identifier')
        password = request.POST.get('password')

        if is_phone_number(login_identifier):
            # It's a phone number, try to get the user by phone
            try:
                user = Profile.objects.get(phone=login_identifier).user
                username = user.username
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'No user found with this phone number.'}, status=404)
        else:
            # It's a username
            username = login_identifier

        # Attempt to authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
