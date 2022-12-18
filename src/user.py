"""
User functions implementation
"""
import urllib.request
import imghdr
import os
import re
import jwt
import requests
from PIL import Image
from flask import request
from error import InputError, AccessError
import data

def user_profile(token, u_id):
    '''
    Return user profile with a given token and user ID
    '''
    valid_user = token_validity(token)

    if not valid_user:
        raise AccessError(description='Cannot find user with provided token')

    valid_u_id = u_id_validity(u_id)

    if not valid_u_id:
        raise InputError(description='Cannot find user with provided u_id')

    for user in data.users:
        if user['u_id'] == u_id:
            profile = {
                'user': { \
                    'u_id': user['u_id'], \
                    'email': user['email'], \
                    'name_first': user['name_first'], \
                    'name_last': user['name_last'], \
                    'handle_str': user['handle_str'], \
                },
            }
            if 'profile_img_url' in user: # pragma: no cover
                profile['user']['profile_img_url'] = user['profile_img_url']
    return profile

def user_profile_setname(token, name_first, name_last):
    '''
    Change user's first and last name
    '''
    change = token_validity(token)

    if not change:
        raise AccessError(description='Cannot find user with provided token')

    name_validity(name_first, name_last)

    change['name_first'] = name_first
    change['name_last'] = name_last

    for user in data.users:
        if user['u_id'] == change['u_id']:
            user = change

    return {
    }

def user_profile_setemail(token, email):
    '''
    Change user's email
    '''
    change = token_validity(token)

    if not change:
        raise AccessError(description='Cannot find user with provided token')

    email_validity(email)

    change['email'] = email

    for user in data.users:
        if user['u_id'] == change['u_id']:
            user = change

    return {
    }

def user_profile_sethandle(token, handle_str):
    '''
    Change user's handle
    '''
    change = token_validity(token)

    if not change:
        raise AccessError(description='Cannot find user with provided token')

    handle_validity(handle_str)


    change['handle_str'] = handle_str

    for user in data.users:
        if user['u_id'] == change['u_id']:
            user = change

    return {}

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end): # pragma: no cover #pylint: disable=too-many-arguments

    '''
    Upload a photo for user
    '''
    change = token_validity(token)
    if not change:
        raise AccessError(description='Cannot find user with provided token')

    response = requests.get(img_url)
    if response.status_code != 200:
        raise InputError(description='Image cannot be retrieved')

    file_name = change['handle_str'] + "pic.jpg"
    path = "./src/static"
    fullpath = os.path.join(path, file_name)
    urllib.request.urlretrieve(img_url, filename=fullpath)
    if imghdr.what(fullpath) != 'jpeg':
        raise InputError(description='Image is not a JPG file')

    image_object = Image.open(fullpath)
    width, height = image_object.size
    size_validity(width, height, x_start, y_start, x_end, y_end)

    image_object = image_object.crop((x_start, y_start, x_end, y_end))
    image_object.save(fullpath)

    for user in data.users:
        if user['u_id'] == change['u_id']:
            #Link saves in user profile
            user['profile_img_url'] = request.host_url + 'static/' + file_name
    return {}

def u_id_validity(u_id):
    '''
    Checks if the u_id is a valid u_id
    '''
    for user in data.users:
        if  user['u_id'] == u_id:
            return user

    return False

def token_validity(token):
    '''
    Checks if the token is a valid token
    '''
    if token not in data.tokens:
        return False

    decoded_info = jwt.decode(token, data.SECRET, algorithms=['HS256'])
    u_id = decoded_info['u_id']

    for user in data.users:
        if  user['u_id'] == u_id:
            associated_user = user
    return associated_user

def name_validity(name_first, name_last):
    '''
    Checks if first or last name is valid length
    '''
    if not 1 <= len(name_first) <= 50:
        raise InputError(description='First name must be between 1 - 50 characters')

    if not 1 <= len(name_last) <= 50:
        raise InputError(description='Last name must be between 1 - 50 characters')

    return True

def email_validity(email):
    '''
    Check if given email is valid
    '''

    if not re.search(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", email):
        raise InputError(description='Email is invalid')

    for user in data.users:
        if user['email'] == email:
            raise InputError(description='Email is already in use')

    return True

def handle_validity(handle_str):
    '''
    Checks if first or last name is valid length
    '''
    if not 3 <= len(handle_str) <= 20:
        raise InputError(description='Handle name must be between 3 - 20 characters')

    for user in data.users:
        if user['handle_str'] == handle_str:
            raise InputError(description='Handle is already in use')
    return True
def size_validity(width, height, x_start, y_start, x_end, y_end): # pragma: no cover #pylint: disable=too-many-arguments

    '''
    Checks if any of x_start, y_start, x_end, y_end are not
    within the dimensions of the image at the URL.
    '''

    if width == 0 or height == 0:
        raise InputError(description='Image is too small to be cropped')
    if x_start < 0 or x_start >= x_end:
        raise InputError(description=f'''
        The crop dimensions values are not within the dimensions of the image. 
        The image dimensions are {width} and {height}.''')
    if y_start < 0 or y_start >= y_end:
        raise InputError(description=f'''
        The crop dimensions values are not within the dimensions of the image. 
        The image dimensions are {width} and {height}.''')
    if x_end > width or y_end > height:
        raise InputError(description=f'''
        The crop dimensions values are not within the dimensions of the image. 
        The image dimensions are {width} and {height}.''')
