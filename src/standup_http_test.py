'''
Tests the standup functions in the server
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest
import other

# Use this fixture to get the URL of the server.
@pytest.fixture
def url():
    '''
    Get URL of the server
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

def test_standup_simple(url):
    '''
    Test to check standup starts
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    u1payload = res.json()

    assert 'token' in u1payload

    #Create channels
    channel1 = {'token' : u1payload['token'], 'name' : 'Fruit Gang!', \
    'is_public' : True}
    res = requests.post(url + 'channels/create', json=channel1)
    channel_id = res.json()
    assert 'channel_id' in channel_id

    message1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "Hello"}
    res = requests.post(url + 'message/send', json=message1)

    #Channel_details
    detail1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail1)
    u1channels = res.json()

    assert u1channels

    #Start standup
    standup = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'length' : 5}
    res = requests.post(url + 'standup/start', json=standup)
    standup1 = res.json()
    assert standup1

    standup_send1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "Hello, this is standup :)"}
    res = requests.post(url + 'standup/send', json=standup_send1)

    other.clear()

def test_standup_with_error(url):
    '''
    Test standup functions with errors
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

    #Create channels
    channel1 = {'token' : u1payload['token'], 'name' : 'Fruit Gang!', \
    'is_public' : True}
    res = requests.post(url + 'channels/create', json=channel1)
    channel_id = res.json()
    assert 'channel_id' in channel_id

    #Invite user2 to channel1
    invite = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], \
    'u_id' : u2payload['u_id']}
    requests.post(url + 'channel/invite', json=invite)

    #Test standup start wrong channel_id error
    standup = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'] + 45, 'length' : 5}
    res = requests.post(url + 'standup/start', json=standup)
    assert res.status_code != 200

    standup = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'length' : 5}
    res = requests.post(url + 'standup/start', json=standup)
    standup1 = res.json()
    assert standup1

    #Test standup in session error
    standup = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'length' : 5}
    res = requests.post(url + 'standup/start', json=standup)
    assert res.status_code != 200

    standup_active = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'standup/active', params=standup_active)
    active1 = res.json()
    assert active1

    #Test standup channel_id error
    standup_active = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'] + 45}
    res = requests.get(url + 'standup/active', params=standup_active)
    assert res.status_code != 200

def test_standup_with_error_next_half(url):
    '''
    The next half of standup error tests
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

    #Create channels
    channel1 = {'token' : u1payload['token'], 'name' : 'Fruit Gang!', \
    'is_public' : True}
    res = requests.post(url + 'channels/create', json=channel1)
    channel_id = res.json()
    assert 'channel_id' in channel_id

    #Invite user2 to channel1
    invite = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], \
    'u_id' : u2payload['u_id']}
    requests.post(url + 'channel/invite', json=invite)

    standup_send2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "Hello, this is user 2 :)"}
    res = requests.post(url + 'standup/send', json=standup_send2)

    #Test standup send member not in channel error
    standup_send3 = {'token' : u3payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "Hello, this is user 3 >:)"}
    res = requests.post(url + 'standup/send', json=standup_send3)
    assert res.status_code != 200

    long_message = '''
        Hi, this is a standup message
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        Beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep
        Boooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooop
        '''

    #Test standup send long message error
    standup_send2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : long_message}
    res = requests.post(url + 'standup/send', json=standup_send2)
    assert res.status_code != 200

    #Test trying to start a session through standup send error
    standup_send2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "/standup:"}
    res = requests.post(url + 'standup/send', json=standup_send2)
    assert res.status_code != 200

    #Test standup send no active session error
    sleep(5)
    standup_send2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'message' : "Hello, this is user 2 :)"}
    res = requests.post(url + 'standup/send', json=standup_send2)
    assert res.status_code != 200
