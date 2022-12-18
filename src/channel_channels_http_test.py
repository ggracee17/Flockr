'''
Tests the channel_invite, channel_details, channels_create,
channels_list and channels_listall functions in the server
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import pytest
import requests

INVALID_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9'

@pytest.fixture
def url():
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
    A simple sanity test to check that the server is set up properly
    '''
    assert url.startswith("http")


def test_channel_channels(url):
    '''Tests the calling of channel and channels functions'''
    # register and login user1
    reg_data = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user1 = response.json()

    # test channels/create
    # user1 creates channel1
    channel_data = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 200
    channel1 = response.json()
    assert 'channel_id' in channel1

    # register and login user2
    reg_data = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user2 = response.json()

    # test channel/invite
    # user1 invites user2 to join channel1
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 200
    assert not response.json()

    # test channel/details
    # check that both user1 and user2 are in channel1
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
    }
    response = requests.get(url + 'channel/details', params=data)
    assert response.status_code == 200

    details = response.json()
    assert 'name' in details
    assert 'owner_members' in details
    assert 'all_members' in details
    owner_list = []
    for owner in details['owner_members']:
        owner_list.append(owner['u_id'])
    assert user1['u_id'] in owner_list
    assert user2['u_id'] not in owner_list
    member_list = []
    for member in details['all_members']:
        member_list.append(member['u_id'])
    assert user1['u_id'] in member_list
    assert user2['u_id'] in member_list

    # user2 creates channel2
    channel_data = {
        'token': user2['token'],
        'name': 'channel2',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 200
    channel2 = response.json()
    assert 'channel_id' in channel2

    # test channels/list
    # check that user1 is part of 1 channel and user2 is part of 2 channels
    response = requests.get(url + 'channels/list', params={'token': user1['token']})
    assert response.status_code == 200
    info = response.json()
    assert 'channels' in info
    assert len(info['channels']) == 1
    response = requests.get(url + 'channels/list', params={'token': user2['token']})
    info = response.json()
    assert len(info['channels']) == 2

    # test channels/listall
    # check that the total number of channels is 2
    response = requests.get(url + 'channels/listall', params={'token': user2['token']})
    assert response.status_code == 200
    info = response.json()
    assert 'channels' in info
    assert len(info['channels']) == 2

def test_invalid_channel_channels(url):
    '''Tests calling channel and channels functions with invalid inputs'''
    # register and login user1
    reg_data = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user1 = response.json()

    # test channels/create
    # user1 creates channel1
    channel_data = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 200
    channel1 = response.json()
    assert 'channel_id' in channel1

    # test create with invalid channel name
    long_name = 'x' * 21
    channel_data = {
        'token': user1['token'],
        'name': long_name,
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 400

    # test create with invalid token
    channel_data = {
        'token': INVALID_TOKEN,
        'name': 'channel2',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 400

    # register and login user2
    reg_data = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user2 = response.json()

    # test channel/invite
    # test invite with invalid channel_id
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'] + 10,
        'u_id': user2['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 400

    # test invite with invalid user id
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'] + 10,
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 400

    # test invite with invalid token
    data = {
        'token': INVALID_TOKEN,
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 400

    # test invite with invalid access
    # user1 cannot invite himself to channel1
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user1['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 400

    # user2 cannot invite user1 to channel1
    data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user1['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 400

    # test details when authorised user is not a member of channel
    data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
    }
    response = requests.get(url + 'channel/details', params=data)
    assert response.status_code == 400

    # user1 invites user2 to join channel1
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    }

    response = requests.post(url + 'channel/invite', json=data)
    assert response.status_code == 200
    assert not response.json()

    # test channel/details
    # check that both user1 and user2 are in channel1
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
    }
    response = requests.get(url + 'channel/details', params=data)
    assert response.status_code == 200

    details = response.json()
    assert 'name' in details
    assert 'owner_members' in details
    assert 'all_members' in details
    owner_list = []
    for owner in details['owner_members']:
        owner_list.append(owner['u_id'])
    assert user1['u_id'] in owner_list
    assert user2['u_id'] not in owner_list
    member_list = []
    for member in details['all_members']:
        member_list.append(member['u_id'])
    assert user1['u_id'] in member_list
    assert user2['u_id'] in member_list

    # test details with invalid channel id
    data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'] + 10,
    }
    response = requests.get(url + 'channel/details', params=data)
    assert response.status_code == 400

    # test details with invalid token
    data = {
        'token': INVALID_TOKEN,
        'channel_id': channel1['channel_id'],
    }
    response = requests.get(url + 'channel/details', params=data)
    assert response.status_code == 400

    # user2 creates channel2
    channel_data = {
        'token': user2['token'],
        'name': 'channel2',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data)
    assert response.status_code == 200
    channel2 = response.json()
    assert 'channel_id' in channel2

    # test channels/list
    # check that user1 is part of 1 channel and user2 is part of 2 channels
    response = requests.get(url + 'channels/list', params={'token': user1['token']})
    assert response.status_code == 200
    info = response.json()
    assert 'channels' in info
    assert len(info['channels']) == 1
    response = requests.get(url + 'channels/list', params={'token': user2['token']})
    info = response.json()
    assert len(info['channels']) == 2

    # test channels list with invalid token
    response = requests.get(url + 'channels/list', params={'token': INVALID_TOKEN})
    assert response.status_code == 400

    # test channels/listall
    # check that the total number of channels is 2
    response = requests.get(url + 'channels/listall', params={'token': user2['token']})
    assert response.status_code == 200
    info = response.json()
    assert 'channels' in info
    assert len(info['channels']) == 2

    # test channels listall with invalid token
    response = requests.get(url + 'channels/listall', params={'token': INVALID_TOKEN})
    assert response.status_code == 400
