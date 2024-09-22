import re


def is_valid_email(email):
    #Validate email format using regex.
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_phone_number(phone):
    #Check if the phone number contains only digits
    return phone.isdigit()

# Feature: Here we can add more validations, for example: phone number for different countries etc... 
