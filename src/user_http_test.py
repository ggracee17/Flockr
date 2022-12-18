'''
Tests the user_profile, user_profile_setname, user_profile_setemail,
user_profile_sethandle and users_all functions in the server
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest

# Use this fixture to get the URL of the server.
@pytest.fixture
def url():
    '''
    Generate url
    '''
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    assert url.startswith("http")

def test_user(url):
    '''
    Tests the calling of user_profile function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    user2 = {'email' : 'cherry@gmail.com', 'password' : 'berrycherry', \
    'name_first' : 'Cherry', 'name_last' : 'Berry'}
    res = requests.post(url + 'auth/register', json=user2)
    u2payload = res.json()

    user3 = {'email' : 'kimi@gmail.com', 'password' : 'kiminokiwi', \
    'name_first' : 'Kimi', 'name_last' : 'Kiwi'}
    res = requests.post(url + 'auth/register', json=user3)
    u3payload = res.json()

    assert 'token' in u1payload and u2payload and u3payload

    #Test user_profile
    detail = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=detail)
    u1profile = res.json()

    assert 'user' in u1profile
    assert 'u_id' in u1profile['user']
    assert 'email' in u1profile['user']
    assert 'name_first' in u1profile['user']
    assert 'name_last' in u1profile['user']
    assert 'handle_str' in u1profile['user']

def test_user_error_token(url):
    '''
    Tests the calling of user_profile function error
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    assert 'token' in u1payload

    detail = {'token' : u1payload['token'] + 'a', 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=detail)
    assert res.status_code != 200

    detail = {'token' : u1payload['token'], 'u_id' : u1payload['u_id'] + 45}
    res = requests.get(url + 'user/profile', params=detail)
    assert res.status_code != 200

def test_user_setname(url):
    '''
    Tests the calling of user_profile_setname function
    '''
    #Create user
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user name
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['name_first'] == 'Anna'
    assert u1profile['user']['name_last'] == 'Banana'

    #Test profile_setname
    detail = {'token' : u1payload['token'], 'name_first' : 'Ben', \
    'name_last' : 'Berry'}
    res = requests.put(url + 'user/profile/setname', json=detail)
    assert not res.json()

    #Check that user name has changed
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['name_first'] == 'Ben'
    assert u1profile['user']['name_last'] == 'Berry'

def test_user_setname_error(url):
    '''
    Tests the calling of user_profile_setname function with error
    '''
    #Create user
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user name
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['name_first'] == 'Anna'
    assert u1profile['user']['name_last'] == 'Banana'

    #Test profile_setname first name short error
    detail = {'token' : u1payload['token'], 'name_first' : '', \
    'name_last' : 'Berry'}
    res = requests.put(url + 'user/profile/setname', json=detail)
    assert res.status_code != 200

    #Test profile_setname last name short error
    detail = {'token' : u1payload['token'], 'name_first' : 'Ben', \
    'name_last' : ''}
    res = requests.put(url + 'user/profile/setname', json=detail)
    assert res.status_code != 200

    long_name = '''
    This is a very long name. This is a very long name. This is a very long name.
    This is a very long name. This is a very long name. This is a very long name.
    This is a very long name. This is a very long name. This is a very long name.
    '''

    #Test profile_setname first name long error
    detail = {'token' : u1payload['token'], 'name_first' : long_name, \
    'name_last' : 'Berry'}
    res = requests.put(url + 'user/profile/setname', json=detail)
    assert res.status_code != 200

    #Test profile_setname last name long error
    detail = {'token' : u1payload['token'], 'name_first' : 'Ben', \
    'name_last' : long_name}
    res = requests.put(url + 'user/profile/setname', json=detail)
    assert res.status_code != 200

def test_user_setemail(url):
    '''
    Tests the calling of user_profile_setemail function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user email
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['email'] == 'anna@gmail.com'

    #Test profile_setemail
    detail = {'token' : u1payload['token'], 'email' : 'banana@yahoo.com'}
    res = requests.put(url + 'user/profile/setemail', json=detail)
    assert not res.json()

    #Check that user email has changed
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['email'] == 'banana@yahoo.com'

def test_user_setemail_error(url):
    '''
    Tests the calling of user_profile_setemail function with error
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user email
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['email'] == 'anna@gmail.com'

    #Test profile_setemail same email error
    detail = {'token' : u1payload['token'], 'email' : 'anna@gmail.com'}
    res = requests.put(url + 'user/profile/setemail', json=detail)
    assert res.status_code != 200

   #Test profile_setemail wrong email format error
    detail = {'token' : u1payload['token'], 'email' : 'Banana@gmail.com'}
    res = requests.put(url + 'user/profile/setemail', json=detail)
    assert res.status_code != 200

def test_user_sethandle(url):
    '''
    Tests the calling of user_profile_setemail function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user handle
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    og_handle = u1profile['user']['handle_str']

    #Test profile_sethandle
    detail = {'token' : u1payload['token'], 'handle_str' : 'bananananana'}
    res = requests.put(url + 'user/profile/sethandle', json=detail)
    assert not res.json()

    #Check that user handle has changed
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    new_handle = u1profile['user']['handle_str']
    assert og_handle != new_handle
    assert new_handle == 'bananananana'

def test_user_sethandle_error(url):
    '''
    Tests the calling of user_profile_setemail function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()
    assert 'token' in u1payload

    #Check user handle
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    og_handle = u1profile['user']['handle_str']

    #Test profile_sethandle long handle error
    detail = {'token' : u1payload['token'], \
    'handle_str' : 'thisislongerthantwentyletters'}
    res = requests.put(url + 'user/profile/sethandle', json=detail)
    assert res.status_code != 200

    #Test profile_sethandle original hangle error
    detail = {'token' : u1payload['token'], \
    'handle_str' : og_handle}
    res = requests.put(url + 'user/profile/sethandle', json=detail)
    assert res.status_code != 200

def test_users_all(url):
    '''
    Tests the calling of users_all function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    user2 = {'email' : 'cherry@gmail.com', 'password' : 'berrycherry', \
    'name_first' : 'Cherry', 'name_last' : 'Berry'}
    res = requests.post(url + 'auth/register', json=user2)
    u2payload = res.json()

    user3 = {'email' : 'kimi@gmail.com', 'password' : 'kiminokiwi', \
    'name_first' : 'Kimi', 'name_last' : 'Kiwi'}
    res = requests.post(url + 'auth/register', json=user3)
    u3payload = res.json()

    assert 'token' in u1payload and u2payload and u3payload

    #Test user_all
    detail = {'token': u1payload['token']}
    res = requests.get(url + 'users/all', params=detail)
    user_data = res.json()
    assert 'users' in user_data
    assert len(user_data['users']) == 3

def test_users_all_error(url):
    '''
    Tests the calling of users_all function
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    assert 'token' in u1payload

    #Test user_all token error
    detail = {'token': u1payload['token'] + 'a'}
    res = requests.get(url + 'users/all', params=detail)
    assert res.status_code != 200

def test_user_upload(url):
    '''
    Tests user_profile upload photo
    '''
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    assert 'token' in u1payload

    detail = {'token': u1payload['token'], \
    'img_url': 'https://ichef.bbci.co.uk/news/800/cpsprodpb/12A9B/production/_111434467_gettyimages-1143489763.jpg', \
    'x_start' : 100, 'y_start': 100, 'x_end' : 500, 'y_end' : 450}
    res = requests.post(url + 'user/profile/uploadphoto', json=detail)
    assert not res.json()

    #Check user profile_img_url exist
    profile = {'token' : u1payload['token'], 'u_id' : u1payload['u_id']}
    res = requests.get(url + 'user/profile', params=profile)
    u1profile = res.json()
    assert u1profile['user']['profile_img_url']

def test_user_upload_error(url):
    '''
    Tests user_profile upload photo
    '''
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    assert 'token' in u1payload

    #Test wrong image dimensions error
    detail = {'token': u1payload['token'], \
    'img_url': 'https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg', \
    'x_start' : 100, 'y_start': 100, 'x_end' : 500, 'y_end' : 450}
    res = requests.post(url + 'user/profile/uploadphoto', json=detail)
    assert res.status_code != 200

    detail = {'token': u1payload['token'], \
    'img_url': 'https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg', \
    'x_start' : 100, 'y_start': 100, 'x_end' : 500, 'y_end' : 500}
    res = requests.post(url + 'user/profile/uploadphoto', json=detail)
    assert res.status_code != 200

    detail = {'token': u1payload['token'], \
    'img_url': 'https://interactive-examples.mdn.mozilla.net/media/cc0-images/grapefruit-slice-332-332.jpg', \
    'x_start' : 100, 'y_start': 100, 'x_end' : 0, 'y_end' : 0}
    res = requests.post(url + 'user/profile/uploadphoto', json=detail)
    assert res.status_code != 200

    #Test invalid url error
    detail = {'token': u1payload['token'], \
    'img_url': 'Picture of a cute cat', \
    'x_start' : 100, 'y_start': 100, 'x_end' : 500, 'y_end' : 450}
    res = requests.post(url + 'user/profile/uploadphoto', json=detail)
    assert res.status_code != 200
