''' Tests the auth functions in the server'''
import signal
import re
from subprocess import Popen, PIPE
from time import sleep
import pytest
import requests
import other

@pytest.fixture
def url():
    '''Gets the url of the server'''
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


def test_server_clear(url):
    '''Tests the calling of other.clear'''

    other.clear()

    response = requests.delete(url + 'clear')
    empty_dict = response.json()
    assert empty_dict == {}

def test_server_admin_userpermission_change(url):
    '''Tests the calling of other.admin_userpermission_change'''

    other.clear()

    # Registers two users
    test_user_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=test_user_in)
    test_user_data = response.json()

    another_user_in = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=another_user_in)
    another_user_data = response.json()

    # Calls the admin_userperimission_change function and tests that it returns
    data_in = {
        'token': test_user_data['token'],
        'u_id': another_user_data['u_id'],
        'permission_id': 1,
    }

    response = requests.post(url + 'admin/userpermission/change', json=data_in)
    user_data = response.json()
    assert user_data == {}

def test_server_admin_userpermission_change_error(url):
    '''Tests the error raising of other.admin_userpermission_change'''

    other.clear()

    # Register a user
    test_user_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=test_user_in)
    test_user_data = response.json()

    # Tests invalid token
    data_in = {
        'token': 'invalid_token',
        'u_id': test_user_data['u_id'],
        'permission_id': 1,
    }
    response = requests.post(url + 'admin/userpermission/change', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests invalid u_id
    data_in = {
        'token': test_user_data['token'],
        'u_id': 33,
        'permission_id': 1,
    }
    response = requests.post(url + 'admin/userpermission/change', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Register another user
    another_user_in = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=another_user_in)
    another_user_data = response.json()

    # Tests invalid permission_id
    data_in = {
        'token': test_user_data['token'],
        'u_id': another_user_data['u_id'],
        'permission_id': 4,
    }
    response = requests.post(url + 'admin/userpermission/change', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests invalid permission_id
    data_in = {
        'token': another_user_data['token'],
        'u_id': test_user_data['u_id'],
        'permission_id': 1,
    }
    response = requests.post(url + 'admin/userpermission/change', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

def test_server_search(url):
    '''Tests the calling of other.search'''

    other.clear()

    # Registers two users
    test_user_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=test_user_in)
    test_user_data = response.json()

    # Calls the search function and tests that it returns
    data_in = {
        'token': test_user_data['token'],
        'query_str': 'key',
    }

    response = requests.get(url + 'search', params=data_in)
    search_data = response.json()
    assert 'messages' in search_data

def test_server_search_error(url):
    '''Tests the error raising of other.search'''

    other.clear()

    # Calls the search function and tests that it returns
    data_in = {
        'token': 'invalid_token',
        'query_str': 'key',
    }

    response = requests.get(url + 'search', params=data_in)
    search_data = response.json()
    assert search_data['code'] == 400