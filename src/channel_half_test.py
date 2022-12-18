'''
Tests for channel_invite(token, channel_id, u_id),
channel_details(token, channel_id), and
channel_messages(token, channel_id, start)
'''

import pytest
import data
from other import clear
import other
import channel
import auth
import channels
import message
import error

def test_invite_details():
    '''
    Tests for valid channels and function calls
    '''
    clear()
    token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2 = add_channel_info()

    with pytest.raises(error.AccessError):
        channel.channel_details(token3, c_id2)

    assert channel.channel_details(token1, c_id1) == {
        'name': 'channel1',
        'owner_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
    }

    channel.channel_invite(token1, c_id1, u_id2)
    assert channel.channel_details(token1, c_id1) == {
        'name': 'channel1',
        'owner_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            },
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            }
        ],
    }
    channel.channel_invite(token2, c_id1, u_id3)
    assert channel.channel_details(token1, c_id1) == {
        'name': 'channel1',
        'owner_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
        ],
        'all_members': [
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            },
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            },
            {
                'u_id': u_id3,
                'name_first' : 'Taylor',
                'name_last' : 'Swift'
            }
        ],
    }

    assert channel.channel_details(token2, c_id2) == {
        'name' : 'channel2',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            }
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            }
        ],
    }
    channel.channel_invite(token2, c_id2, u_id1)
    assert channel.channel_details(token2, c_id2) == {
        'name' : 'channel2',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            },
            {
                'u_id': u_id1,
                'name_first' : 'Hayden',
                'name_last' : 'Jacobs'
            }
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            },
            {
                'u_id': u_id1,
                'name_first' : 'Hayden',
                'name_last' : 'Jacobs'
            }
        ],
    }
    channel.channel_invite(token2, c_id2, u_id3)
    assert channel.channel_details(token2, c_id2) == {
        'name' : 'channel2',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            },
            {
                'u_id': u_id1,
                'name_first' : 'Hayden',
                'name_last' : 'Jacobs'
            }
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first' : 'Sam',
                'name_last' : 'Smith'
            },
            {
                'u_id': u_id1,
                'name_first' : 'Hayden',
                'name_last' : 'Jacobs'
            },
            {
                'u_id': u_id3,
                'name_first' : 'Taylor',
                'name_last' : 'Swift'
            }
        ],
    }

def test_invalid_id():
    '''
    Tests for invalid channel ids or user ids
    '''
    clear()
    token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2 = add_channel_info()
    with pytest.raises(error.InputError):
        channel.channel_invite(token1, len(data.channels) + 1, u_id2)
    with pytest.raises(error.InputError):
        channel.channel_invite(token2, -1, u_id1)
    with pytest.raises(error.InputError):
        channel.channel_invite(token2, 0, u_id3)
    with pytest.raises(error.InputError):
        channel.channel_details(token1, 99)
    with pytest.raises(error.InputError):
        channel.channel_details(token1, 3)
    with pytest.raises(error.InputError):
        channel.channel_details(token2, -1)
    with pytest.raises(error.InputError):
        channel.channel_details(token3, 0)
    with pytest.raises(error.InputError):
        channel.channel_invite(token1, c_id1, len(data.users) + 1)
    with pytest.raises(error.InputError):
        channel.channel_invite(token2, c_id2, 0)
    with pytest.raises(error.InputError):
        channel.channel_invite(token2, c_id2, -2)

def test_already_joined():
    '''
    Tests for invalid invitations into channels already joined
    '''
    clear()
    token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2 = add_channel_info()

    # invite user3 to join channel2
    channel.channel_invite(token2, c_id2, u_id3)
    with pytest.raises(error.InputError):
        channel.channel_invite(token1, c_id1, u_id1)
    with pytest.raises(error.InputError):
        channel.channel_invite(token2, c_id2, u_id3)
    with pytest.raises(error.InputError):
        channel.channel_invite(token3, c_id2, u_id2)

def test_invite_global_owner():
    '''
    Tests for the promotion of invited global owners to channel owners
    '''
    clear()

    #Creates new users and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token1 = user1['token']
    u_id2 = user2['u_id']
    other.admin_userpermission_change(token1, u_id2, 1)

    #Adds global owner to channel
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    channel.channel_invite(token1, new_channel, u_id2)
    is_owner = False

    #Checks global owner is channel owner
    owners = channel.channel_details(token1, new_channel)['owner_members']
    for owner in owners:
        if owner['u_id'] == u_id2:
            is_owner = True

    assert is_owner

def test_invalid_access():
    '''
    Tests for invalid access
    '''

    clear()
    token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2 = add_channel_info()
    with pytest.raises(error.AccessError):
        channel.channel_invite(token1, c_id2, u_id3)
    with pytest.raises(error.AccessError):
        channel.channel_invite(token3, c_id1, u_id3)
    with pytest.raises(error.AccessError):
        channel.channel_invite(token2, c_id1, u_id2)
    with pytest.raises(error.AccessError):
        channel.channel_invite(token3, c_id2, u_id1)
    with pytest.raises(error.AccessError):
        channel.channel_details(token1, c_id2)
    with pytest.raises(error.AccessError):
        channel.channel_details(token2, c_id1)

def test_channel_messages():
    '''
    Tests for getting messages from channel
    '''
    clear()
    # setting up users, channels and messages
    token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2 = add_channel_info()

    # user1 sends 3 messages to channel1
    message.message_send(token1, c_id1, 'Hello World')
    message.message_send(token1, c_id1, 'Goodbye')
    message.message_send(token1, c_id1, 'Happy Birthday')

    msg_list = channel.channel_messages(token1, c_id1, 0)
    assert len(msg_list['messages']) == 3
    msg0 = msg_list['messages'][0]
    assert msg0['message_id'] == 3
    assert msg0['u_id'] == u_id1
    assert msg0['message'] == 'Happy Birthday'
    msg1 = msg_list['messages'][1]
    assert msg1['message_id'] == 2
    assert msg1['u_id'] == u_id1
    assert msg1['message'] == 'Goodbye'
    msg2 = msg_list['messages'][2]
    assert msg2['message_id'] == 1
    assert msg2['u_id'] == u_id1
    assert msg2['message'] == 'Hello World'
    assert msg_list['start'] == 0
    assert msg_list['end'] == -1

    # user2 sends 2 identical messages to channel2
    message.message_send(token2, c_id2, 'Hello World')
    message.message_send(token2, c_id2, 'Hello World')
    msg_list = channel.channel_messages(token2, c_id2, 0)
    assert len(msg_list['messages']) == 2
    msg0 = msg_list['messages'][0]
    assert msg0['message_id'] == 5
    assert msg0['u_id'] == u_id2
    assert msg0['message'] == 'Hello World'
    msg1 = msg_list['messages'][1]
    assert msg1['message_id'] == 4
    assert msg1['u_id'] == u_id2
    assert msg1['message'] == 'Hello World'

    with pytest.raises(error.AccessError):
        channel.channel_messages(token2, c_id1, 0)
    with pytest.raises(error.AccessError):
        channel.channel_messages(token3, c_id1, 0)
    with pytest.raises(error.AccessError):
        message.message_send(token3, c_id2, 'Goodbye')

    # invite user3 into channel2 and user3 sends a message
    channel.channel_invite(token2, c_id2, u_id3)
    message.message_send(token3, c_id2, 'Goodbye')
    msg_list = channel.channel_messages(token2, c_id2, 0)
    assert len(msg_list['messages']) == 3
    msg0 = msg_list['messages'][0]
    assert msg0['message_id'] == 6
    assert msg0['u_id'] == u_id3
    assert msg0['message'] == 'Goodbye'

def test_invalid_channel():
    '''
    Tests for invalid channel ids and start, end values of channel_messages calls
    '''
    clear()
    with pytest.raises(error.InputError):
        channel.channel_invite(1, 1, 2)

    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    u_id1 = user1['u_id']

    with pytest.raises(error.InputError):
        channel.channel_invite(token1, 1, 2)

    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    token2 = user2['token']
    u_id2 = user2['u_id']

    with pytest.raises(error.InputError):
        channel.channel_invite(token1, 1, u_id2)

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    channel.channel_invite(token1, c_id1, u_id2)
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']

    auth.auth_logout(token2)
    with pytest.raises(error.AccessError):
        channel.channel_invite(token2, c_id2, u_id1)

    message1 = 'Hello World'
    message2 = 'Goodbye'
    message3 = 'Happy Birthday'
    msg1 = message.message_send(token1, c_id1, message1)
    message.message_send(token1, c_id1, message2)
    message.message_send(token1, c_id1, message3)
    with pytest.raises(error.AccessError):
        message.message_send(token2, c_id2, message1)
    with pytest.raises(error.AccessError):
        message.message_remove(token2, msg1['message_id'])

    auth.auth_login('another@email.com', 'another_password')
    message.message_send(token2, c_id2, message1)
    message.message_send(token2, c_id2, message2)

    # test input error for invalid channel ids and start values
    with pytest.raises(error.InputError):
        channel.channel_messages(token1, 99, 0)
    with pytest.raises(error.InputError):
        channel.channel_messages(token1, 0, 0)
    with pytest.raises(error.AccessError):
        channel.channel_messages(token1, c_id2, 0)
    with pytest.raises(error.InputError):
        channel.channel_messages(token1, c_id1, 10)

def test_more_than_50_messages():
    '''
    Tests for when there are more than 50 messages in the channel
    '''
    clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # send 51 messages to channel1
    num_msg = 0
    while num_msg <= 50:
        message.message_send(token1, c_id1, 'Hello World')
        num_msg += 1

    msg_list = channel.channel_messages(token1, c_id1, 0)
    assert len(msg_list['messages']) == 50
    assert msg_list['start'] == 0
    assert msg_list['end'] == 50

def add_channel_info():
    '''
    Functions to register and login users
    '''
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    u_id1 = user1['u_id']

    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    token2 = user2['token']
    u_id2 = user2['u_id']

    user3 = auth.auth_register('final@email.com', 'final_password', 'Taylor', 'Swift')
    token3 = user3['token']
    u_id3 = user3['u_id']

    # create channels
    channel1 = channels.channels_create(token1, 'channel1', True)
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id1 = channel1['channel_id']
    c_id2 = channel2['channel_id']

    return token1, token2, token3, u_id1, u_id2, u_id3, c_id1, c_id2
    