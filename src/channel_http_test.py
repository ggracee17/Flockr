'''
Tests the channel_leave, channel_join, channel_addowner and
channel_removeowner functions in the server
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import pytest

INVALID_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'

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

def test_channel(url):
    '''
    Tests the calling of channel leave, join, addowner and removeowner functions
    '''
    #Create users
    user1 = {'email' : 'anna@gmail.com', 'password' : 'annabanana', \
    'name_first' : 'Anna', 'name_last' : 'Banana'}
    res = requests.post(url + 'auth/register', json=user1)
    assert res.status_code == 200
    u1payload = res.json()

    user2 = {'email' : 'cherry@gmail.com', 'password' : 'berrycherry', \
    'name_first' : 'Cherry', 'name_last' : 'Berry'}
    res = requests.post(url + 'auth/register', json=user2)
    assert res.status_code == 200
    u2payload = res.json()

    user3 = {'email' : 'kimi@gmail.com', 'password' : 'kiminokiwi', \
    'name_first' : 'Kimi', 'name_last' : 'Kiwi'}
    res = requests.post(url + 'auth/register', json=user3)
    assert res.status_code == 200
    u3payload = res.json()

    assert 'token' in u1payload and u2payload and u3payload

    #Test create channels
    channel1 = {'token' : u1payload['token'], 'name' : 'Fruit Gang!', \
    'is_public' : True}
    res = requests.post(url + 'channels/create', json=channel1)
    assert res.status_code == 200
    channel_id = res.json()
    assert 'channel_id' in channel_id

    #Test channel_invite
    #Invite user2 to channel1
    invite = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], \
    'u_id' : u2payload['u_id']}
    res = requests.post(url + 'channel/invite', json=invite)
    assert res.status_code == 200

    #Test channel_details
    detail1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail1)
    assert res.status_code == 200
    u1channels = res.json()
    assert u1channels

    detail2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail2)
    assert res.status_code == 200
    u2channels = res.json()

    #Test channel_leave
    #User2 leave channel1
    channel_leave = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/leave', json=channel_leave)
    assert res.status_code == 200
    assert not res.json()
    res = requests.get(url + 'channels/list', params={'token' : u2payload['token']})
    assert res.status_code == 200
    u2list = res.json()
    assert not u2list['channels']

    #Test channel_addowner
    #Add user3 to be an owner of channel1
    channel_addowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/addowner', json=channel_addowner)
    assert res.status_code == 200
    assert not res.json()
    res = requests.get(url + 'channels/list', params={'token' : u3payload['token']})
    assert res.status_code == 200
    u3list = res.json()
    assert u3list['channels']
    detail3 = {'token' : u3payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail3)
    assert res.status_code == 200
    u3channels = res.json()
    assert(len(u3channels['owner_members'])) == 2

    #Test channel_join
    #User2 join channel1
    channel_join = {'token' : u2payload['token'], 'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/join', json=channel_join)
    assert res.status_code == 200
    assert not res.json()
    res = requests.get(url + 'channel/details', params=detail2)
    assert res.status_code == 200
    u2channels = res.json()
    assert (len(u2channels['owner_members'])) == 2
    assert (len(u2channels['all_members'])) == 3

    #Test channel_removeowner
    #Remove user3 as owner of channel1
    channel_removeowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/removeowner', json=channel_removeowner)
    assert res.status_code == 200
    assert not res.json()
    detail1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail1)
    assert res.status_code == 200
    u1channels = res.json()
    assert(len(u1channels['owner_members'])) == 1

def test_channel_invalid_inputs(url):
    '''
    Tests the calling of channel leave, join, addowner and
    removeowner functions with invalid inputs

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

    #Test create channels
    channel1 = {'token' : u1payload['token'], 'name' : 'Fruit Gang!', \
    'is_public' : True}
    res = requests.post(url + 'channels/create', json=channel1)
    channel_id = res.json()
    assert 'channel_id' in channel_id

    #Test channel_invite
    #Invite user2 to channel1
    invite = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], \
    'u_id' : u2payload['u_id']}
    requests.post(url + 'channel/invite', json=invite)

    #Test channel_details
    detail1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail1)
    u1channels = res.json()
    assert u1channels

    detail2 = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail2)
    u2channels = res.json()

    #Test channel_leave
    #Test invalid channel id
    channel_leave = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'] + 10}
    res = requests.post(url + 'channel/leave', json=channel_leave)
    assert res.status_code == 400

    #Test invalid token
    channel_leave = {'token' : INVALID_TOKEN, \
    'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/leave', json=channel_leave)
    assert res.status_code == 400

    #User2 leave channel1
    channel_leave = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/leave', json=channel_leave)
    assert res.status_code == 200

    res = requests.get(url + 'channels/list', params={'token' : u2payload['token']})
    u2list = res.json()
    assert not u2list['channels']

    #Test access error when user2 leaves channel1 again
    channel_leave = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/leave', json=channel_leave)
    assert res.status_code == 400

    #Test channel_addowner
    #Test invalid channel_id
    channel_addowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'] + 10, 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/addowner', json=channel_addowner)
    assert res.status_code == 400

    #Test invalid token
    channel_addowner = {'token' : INVALID_TOKEN, \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/addowner', json=channel_addowner)
    assert res.status_code == 400

    #User1 add user3 to be an owner of channel1
    channel_addowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    requests.post(url + 'channel/addowner', json=channel_addowner)
    res = requests.get(url + 'channels/list', params={'token' : u3payload['token']})
    u3list = res.json()
    assert u3list['channels']
    detail3 = {'token' : u3payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail3)
    u3channels = res.json()
    assert(len(u3channels['owner_members'])) == 2

    #Test when user3 is already an owner
    res = requests.post(url + 'channel/addowner', json=channel_addowner)
    assert res.status_code == 400

    #Test channel_join
    #Test invalid channel_id
    channel_join = {'token' : u2payload['token'], 'channel_id' : channel_id['channel_id'] + 10}
    res = requests.post(url + 'channel/join', json=channel_join)
    assert res.status_code == 400

    #Test invalid token
    channel_join = {'token' : INVALID_TOKEN, 'channel_id' : channel_id['channel_id']}
    res = requests.post(url + 'channel/join', json=channel_join)
    assert res.status_code == 400

    #Create a private channel
    channel2 = {'token' : u1payload['token'], 'name' : 'Private Channel', \
    'is_public' : False}
    res = requests.post(url + 'channels/create', json=channel2)
    channel_id2 = res.json()
    assert 'channel_id' in channel_id2

    #Test error when join a private channel
    channel_join = {'token' : u2payload['token'], 'channel_id' : channel_id2['channel_id']}
    res = requests.post(url + 'channel/join', json=channel_join)
    assert res.status_code == 400

    #User2 join channel1
    channel_join = {'token' : u2payload['token'], 'channel_id' : channel_id['channel_id']}
    requests.post(url + 'channel/join', json=channel_join)
    res = requests.get(url + 'channel/details', params=detail2)
    u2channels = res.json()
    assert (len(u2channels['owner_members'])) == 2
    assert (len(u2channels['all_members'])) == 3

    #Test channel_removeowner
    #Test invalid channel_id
    channel_removeowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'] + 10, 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/removeowner', json=channel_removeowner)
    assert res.status_code == 400

    #Test invalid token
    channel_removeowner = {'token' : INVALID_TOKEN, \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/removeowner', json=channel_removeowner)
    assert res.status_code == 400

    #Test user2 cannot remove owner of channel1 because user2 is not an owner
    channel_removeowner = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/removeowner', json=channel_removeowner)
    assert res.status_code == 400

    #Remove user3 as owner of channel1
    channel_removeowner = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    requests.post(url + 'channel/removeowner', json=channel_removeowner)
    detail1 = {'token' : u1payload['token'], \
    'channel_id' : channel_id['channel_id']}
    res = requests.get(url + 'channel/details', params=detail1)
    u1channels = res.json()
    assert(len(u1channels['owner_members'])) == 1

    #User3 cannot be removed as owner again
    res = requests.post(url + 'channel/removeowner', json=channel_removeowner)
    assert res.status_code == 400

    #Test user2 cannot add owner to channel1 because user2 is not an owner
    channel_addowner = {'token' : u2payload['token'], \
    'channel_id' : channel_id['channel_id'], 'u_id' : u3payload['u_id']}
    res = requests.post(url + 'channel/addowner', json=channel_addowner)
    assert res.status_code == 400
