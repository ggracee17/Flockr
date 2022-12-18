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


def test_auth(url):
    '''Tests the calling of auth_login, logout, and register'''

    other.clear()

    # Tests the calling of auth_register
    data_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert 'u_id' in user_data
    assert 'token' in user_data

    # Tests the calling of auth_login
    data_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
    }
    response2 = requests.post(url + 'auth/login', json=data_in)
    login_data = response2.json()
    assert 'u_id' in login_data
    assert 'token' in login_data

    # Tests the calling of auth_logout
    data_in = {
        'token': user_data['token']
    }
    response3 = requests.post(url + 'auth/logout', json=data_in)
    logout_data = response3.json()
    assert logout_data['is_success']

def test_auth_login_error(url):
    '''Tests the error raising of auth_login'''

    other.clear()

    # Tests invalid email
    data_in = {
        'email': 'email',
        'password': 'test_pass',
    }
    response = requests.post(url + 'auth/login', json=data_in)
    login_data = response.json()
    assert login_data['code'] == 400

    # Tests unregistered email
    data_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
    }
    response = requests.post(url + 'auth/login', json=data_in)
    login_data = response.json()
    assert login_data['code'] == 400

    # Tests wrong password
    data_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    requests.post(url + 'auth/register', json=data_in)
    data_in = {
        'email': 'test@email.com',
        'password': 'wrong_pass',
    }
    response = requests.post(url + 'auth/login', json=data_in)
    login_data = response.json()
    assert login_data['code'] == 400

def test_auth_logout_error(url):
    '''Tests incorrect use of auth_login'''
    
    other.clear()

    # Tests invalid token
    data_in = {
        'token': 'invalid_token'
    }
    response = requests.post(url + 'auth/logout', json=data_in)
    logout_data = response.json()
    assert not logout_data['is_success']

def test_auth_register_error(url):
    '''Tests the error raising of auth_register'''

    other.clear()

    # Tests invalid email
    data_in = {
        'email': 'email',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests already registered email
    data_in = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    requests.post(url + 'auth/register', json=data_in)
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests short password
    data_in = {
        'email': 'another@email.com',
        'password': 'pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests short first name
    data_in = {
        'email': 'another@email.com',
        'password': 'test_pass',
        'name_first': '',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests long first name
    data_in = {
        'email': 'another@email.com',
        'password': 'test_pass',
        'name_first': 'An incredibly long name that is sure to exceed 50 characters',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests short last name
    data_in = {
        'email': 'another@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': '',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

    # Tests long last name
    data_in = {
        'email': 'another@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'An incredibly long name that is sure to exceed 50 characters',
    }
    response = requests.post(url + 'auth/register', json=data_in)
    user_data = response.json()
    assert user_data['code'] == 400

def test_auth_passwordreset(url):
    '''Tests the calling of password reset functions'''

    other.clear()

    # Registers a user to test with
    data_in = {
        'email': 'flockrtestuser@gmail.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=data_in)

    # Tests calling the auth_passwordreset_request function
    data_in = {
        'email': 'flockrtestuser@gmail.com'
    }
    response = requests.post(url + 'auth/passwordreset/request', json=data_in)
    output = response.json()
    assert output == {}

    # Tests calling the auth_passwordreset_reset function
    data_in = {
        'reset_code': 'invalid_reset_code',
        'new_password': 'test_pass'
    }
    response = requests.post(url + 'auth/passwordreset/reset', json=data_in)
    output = response.json()
    assert output['code'] == 400

def test_auth_passwordreset_reset_error(url):
    '''Tests the error raising of auth_passwordreset_reset'''

    other.clear()

    # Tests invalid password
    data_in = {
        'reset_code': 'invalid_reset_code',
        'new_password': 'pass'
    }
    response = requests.post(url + 'auth/passwordreset/reset', json=data_in)
    output = response.json()
    assert output['code'] == 400
