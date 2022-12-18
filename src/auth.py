"""Authentication functions"""

import re
import string
import random
import smtplib
import ssl
import jwt
import data
from error import InputError

def auth_login(email, password):
    """Logs in the user using their email and password"""

    u_id = ''

    token = ''

    email_exists = False

    # Checks the list of users for a user with a matching email
    for user in data.users:
        if email == user['email']:
            # If the correct password was given, a token is issued if the user doesn't have one
            # Otherwise, an input error is raised
            if password == user['password']:
                u_id = user['u_id']
                token = jwt.encode({'u_id': user['u_id']}, data.SECRET,
                                   algorithm='HS256').decode('utf-8')
                if token not in data.tokens:
                    data.tokens.append(token)
            else:
                raise InputError(description='Incorrect password')
            email_exists = True

    # If no user with a matching email is found, an Input error is raised
    if email_exists is False:
        raise InputError(description='Email not registered')


    return {
        'u_id': u_id,
        'token': token,
    }

def auth_logout(token):
    """Logs out the user given their token"""

    # Checks the token list for the token and then removes it and returns true
    # Otherwise, returns false

    if token in data.tokens:
        data.tokens.remove(token)
        return {
            'is_success': True,
        }

    return {
        'is_success': False,
    }

def auth_register(email, password, name_first, name_last):
    """Registers the user if their emal isn't taken
    otherwise, return an error"""

    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    # Input error if not a valid email
    if re.search(regex, email) is None:
        raise InputError(description='Invalid email')

    # Input error if a user already has the given email
    for user in data.users:
        if email == user['email']:
            raise InputError(description='Email already taken')

    # Input error if the password is less than 6 characters long
    if len(password) < 6:
        raise InputError(description='Password too short')

    # Input error if user's first name is not between 1 and 50 characters long
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description='First name too long or short')

    # Input error if user's last name is not between 1 and 50 characters long
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description='Last name too long or short')

    new_handle = name_first + name_last
    handle_str = new_handle[:20]

    handle_str = handle_modify(handle_str)

    user = {
        'u_id': len(data.users) + 1,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle_str,
        'password': password,
        'permission_id': 2,
    }

    # Issues the user's token
    token = jwt.encode({'u_id': user['u_id']}, data.SECRET,
                       algorithm='HS256').decode('utf-8')

    data.tokens.append(token)

    # Gives the first user global owner permissions
    if user['u_id'] == 1:
        user['permission_id'] = 1

    data.users.append(user)

    return {
        'u_id': user['u_id'],
        'token': token,
    }

def auth_passwordreset_request(email): # pragma: no cover
    '''Sends a reset code to the given email if valid'''

    for user in data.users:
        if email == user['email']:
            # Generates a reset code that doesn't already exist
            reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            while reset_code in data.reset_codes:
                reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

            # Removes previous reset code for that user if unused
            old_code = ''
            for code in data.reset_codes:
                if data.reset_codes[code] == email:
                    old_code = code

            if old_code != '':
                del data.reset_codes[old_code]

            # Stores the reset code
            data.reset_codes[reset_code] = email

            # Sends the email
            port = 465
            smtp_server = "smtp.gmail.com"
            sender_email = "flockrtestuser@gmail.com"
            receiver_email = email
            password = "FlockrTestUser"
            message = """\
Subject: Flockr Password Reset Code

Your reset code is: """ + reset_code
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)

    return {}

def auth_passwordreset_reset(reset_code, new_password): # pragma: no cover
    '''Updates a user's password using the reset code they received'''

    # Checks that the new passowrd is valid and the reset code exists
    if reset_code not in data.reset_codes:
        raise InputError(description='Invalid reset code')
    
    if len(new_password) < 6:
        raise InputError(description='New password too short')

    # Gets the email associated with the reset code and then removes the entry
    email = data.reset_codes[reset_code]
    del data.reset_codes[reset_code]

    # Updates the user's password
    for user in data.users:
        if email == user['email']:
            user['password'] = new_password

    return {}

def handle_modify(handle_str):
    '''Modifies taken handles'''
    i = 1

    # If the handle is taken, the last 1 or 2 characters are replaced with a number between 1 and 99
    # Starting at 1 and increasing each time a user is found with the new handle
    while True:
        initial = i
        for user in data.users:
            if user['handle_str'] == handle_str:
                if i < 10:
                    handle_str = handle_str[:19] + str(i)
                else:
                    handle_str = handle_str[:18] + str(i)
                i = i + 1
        if initial == i:
            break

    return handle_str
