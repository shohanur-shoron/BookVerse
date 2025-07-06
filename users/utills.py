from django.contrib.auth.models import User
import random
import string
import re


def generate_unique_username(first_name='shoron', last_name='rahman'):
    username = f"{first_name.lower()}{last_name.lower()}"
    username = username.replace(" ", "")
    if not User.objects.filter(username=username).exists():
        return username
    while True:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        new_username = f"{username}{random_string}"
        if not User.objects.filter(username=new_username).exists():
            return new_username


def is_phone_number(input_string):
    input_string = input_string.strip()

    pattern_01 = r'^01\d{9}$'
    pattern_880 = r'^\+880\d{10}$'

    if re.match(pattern_01, input_string) or re.match(pattern_880, input_string):
        return True

    if re.search(r'[a-zA-Z]', input_string):
        return False

    return False