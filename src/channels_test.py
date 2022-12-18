'''
Tests for channels_create(token, name, is_public),
channels_list(token), channels_listall(token)
'''

import pytest
import data
from other import clear
import channel
import auth
import channels
import error

def test_simple_channel():
    '''
    Tests for when no channel, one channel or two channels has been created
    '''
    clear()
    token1, token2, u_id1, u_id2 = add_user_info()

    assert channels.channels_list(token1) == {
        'channels': [],
    }
    assert channels.channels_listall(token2) == {
        'channels': [],
    }

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

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
    assert data.channels[-1]['is_public']

    assert channels.channels_list(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            }
        ],
    }

    assert channels.channels_listall(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            }
        ],
    }

    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']

    assert channel.channel_details(token2, c_id2) == {
        'name': 'channel2',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            }
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            }
        ],
    }

def test_valid_name():
    '''
    Tests for creating channels with valid name
    '''
    clear()
    token1, token2, u_id1, u_id2 = add_user_info()

    channel2 = channels.channels_create(token2, 'justtt_20_characters', False)
    c_id2 = channel2['channel_id']
    assert channel.channel_details(token2, c_id2) == {
        'name': 'justtt_20_characters',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            }
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            }
        ],
    }
    assert not data.channels[-1]['is_public']

    channel1 = channels.channels_create(token1, 'Test_Channel', True)
    c_id1 = channel1['channel_id']
    assert channel.channel_details(token1, c_id1) == {
        'name': 'Test_Channel',
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
    assert data.channels[-1]['is_public']


def test_multiple_channels():
    '''
    Tests for when multiple channels have been created
    '''
    clear()
    token1, token2, u_id1, u_id2 = add_user_info()
    channels.channels_create(token1, 'channel1', True)
    assert data.channels[-1]['is_public']

    channel2 = channels.channels_create(token2, 'justtt_20_characters', False)
    c_id2 = channel2['channel_id']
    assert not data.channels[-1]['is_public']

    channel3 = channels.channels_create(token1, 'channel3', True)
    c_id3 = channel3['channel_id']
    assert channel.channel_details(token1, c_id3) == {
        'name': 'channel3',
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
    assert data.channels[-1]['is_public']

    assert channels.channels_list(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            },
            {
                'channel_id': 3,
                'name': 'channel3'
            }
        ],
    }

    # invites user1 to join channel2
    channel.channel_invite(token2, c_id2, u_id1)
    assert channels.channels_list(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            },
            {
                'channel_id': 2,
                'name': 'justtt_20_characters'
            },
            {
                'channel_id': 3,
                'name': 'channel3'
            },
        ],
    }

    assert channel.channel_details(token2, c_id2) == {
        'name': 'justtt_20_characters',
        'owner_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            },
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            },
        ],
        'all_members': [
            {
                'u_id': u_id2,
                'name_first': 'Sam',
                'name_last': 'Smith',
            },
            {
                'u_id': u_id1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            },
        ],
    }

    assert channels.channels_listall(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            },
            {
                'channel_id': 2,
                'name': 'justtt_20_characters'
            },
            {
                'channel_id': 3,
                'name': 'channel3'
            },
        ],
    }

def test_invalid_name():
    '''
    Tests for creating channels with invalid name
    '''
    clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']

    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    token2 = user2['token']

    with pytest.raises(error.InputError):
        channels.channels_create(token1, 'very_long_channel_name', True)
    with pytest.raises(error.InputError):
        channels.channels_create(token2, 'more_than_20_characters', False)
    with pytest.raises(error.InputError):
        channels.channels_create(token1, 'abcdefghijklmnopqrstuvwxyz', False)

def test_unjoined_channels():
    '''
    Tests for inviting users into unjoined channels
    then printing details of their joined channels
    '''
    clear()
    token1, token2, u_id1, u_id2 = add_user_info()
    user3 = auth.auth_register('final@email.com', 'final_password', 'Sam', 'Smith')
    token3 = user3['token']
    u_id3 = user3['u_id']

    # create channels
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']
    channel3 = channels.channels_create(token3, 'channel3', True)
    c_id3 = channel3['channel_id']

    # invite user3 to join channel1, user2 to join channel3, user1 to join channel2
    channel.channel_invite(token1, c_id1, u_id3)
    channel.channel_invite(token3, c_id3, u_id2)
    channel.channel_invite(token2, c_id2, u_id1)

    assert channels.channels_list(token1) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            },
            {
                'channel_id': 2,
                'name': 'channel2'
            },
        ],
    }

    assert channels.channels_list(token2) == {
        'channels': [
            {
                'channel_id': 2,
                'name': 'channel2'
            },
            {
                'channel_id': 3,
                'name': 'channel3'
            }
        ],
    }

    assert channels.channels_list(token3) == {
        'channels': [
            {
                'channel_id': 1,
                'name': 'channel1'
            },
            {
                'channel_id': 3,
                'name': 'channel3'
            }
        ],
    }

def test_invalid_token():
    '''
    Tests for invalid tokens
    '''
    clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    auth.auth_logout(user1['token'])

    with pytest.raises(error.AccessError):
        channels.channels_list('invalid_token')
    with pytest.raises(error.AccessError):
        channels.channels_list(user1['token'])

def add_user_info():
    '''
    Function to register and login users
    '''
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    u_id1 = user1['u_id']

    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    token2 = user2['token']
    u_id2 = user2['u_id']

    return token1, token2, u_id1, u_id2
    