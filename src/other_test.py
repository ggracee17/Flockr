'''Tests all the functions in other.py'''

import pytest
import auth
import channel
import channels
import message
import other
from error import InputError, AccessError

def test_clear():
    '''Tests the intended uses of the clear() function'''

    assert other.clear() == {}

    # Registers 3 users
    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    another_token = auth.auth_register('another@email.com', 'another_password',
                                       'another_first', 'another_last')['token']

    final_token = auth.auth_register('final@email.com', 'final_password',
                                     'final_first', 'final_last')['token']

    # Creates 3 channels
    channels.channels_create(test_token, 'channel1', True)
    channels.channels_create(another_token, 'channel2', False)
    channels.channels_create(final_token, 'channel3', True)

    assert other.clear() == {}

    # Checks that the users list has been cleared by registering a user with a
    # previously taken email address
    assert auth.auth_register('test@email.com', 'test_password',
                              'test_first', 'test_last')

    # Checks there are no channels
    assert channels.channels_listall(test_token)['channels'] == []

def test_one_user():
    '''
    Tests for when there is only one user in the system for users_all()
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    user1 = auth.auth_login('test@email.com', 'test_password')
    token1 = user1['token']
    assert other.users_all(token1) == {
        'users': [
            {
                'u_id': 1,
                'email': 'test@email.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'HaydenJacobs',
            },
        ],
    }

def test_multiple_users():
    '''
    Tests for when there are multiple users in the system for users_all()
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    user1 = auth.auth_login('test@email.com', 'test_password')
    token1 = user1['token']
    u_id1 = user1['u_id']
    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    user2 = auth.auth_login('another@email.com', 'another_password')
    token2 = user2['token']
    u_id2 = user2['u_id']
    user3 = auth.auth_register('final@email.com', 'final_password', 'Taylor', 'Swift')
    user3 = auth.auth_login('final@email.com', 'final_password')
    u_id3 = user3['u_id']

    assert other.users_all(token1) == {
        'users': [
            {
                'u_id': u_id1,
                'email': 'test@email.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'HaydenJacobs',
            },
            {
                'u_id': u_id2,
                'email': 'another@email.com',
                'name_first': 'Sam',
                'name_last': 'Smith',
                'handle_str': 'SamSmith',
            },
            {
                'u_id': u_id3,
                'email': 'final@email.com',
                'name_first': 'Taylor',
                'name_last': 'Swift',
                'handle_str': 'TaylorSwift',
            },
        ],
    }
    assert other.users_all(token2) == {
        'users': [
            {
                'u_id': u_id1,
                'email': 'test@email.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'HaydenJacobs',
            },
            {
                'u_id': u_id2,
                'email': 'another@email.com',
                'name_first': 'Sam',
                'name_last': 'Smith',
                'handle_str': 'SamSmith',
            },
            {
                'u_id': u_id3,
                'email': 'final@email.com',
                'name_first': 'Taylor',
                'name_last': 'Swift',
                'handle_str': 'TaylorSwift',
            },
        ],
    }

def test_user_all_invalid_token():
    '''
    Tests for user_all is given invalid token
    '''
    other.clear()
    user1 = auth.auth_register('user1@email.com', 'password1', 'First1', 'Last1')
    token1 = user1['token']
    with pytest.raises(AccessError):
        other.users_all(token1 + 'a')


def test_admin_userpermission_change():
    '''Tests the intended uses of the admin_userpermission_change() function'''
    other.clear()

    # Registers 2 users
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    # Creates 3 channels
    channel1_id = channels.channels_create(test_dict['token'], 'channel1', True)['channel_id']
    channel2_id = channels.channels_create(test_dict['token'], 'channel3', True)['channel_id']
    channels.channels_create(another_dict['token'], 'channel3', True)

    # Joins another_user to the first channel
    channel.channel_join(another_dict['token'], channel1_id)

    # Promotes another_user
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}

    # Checks that the another_user has owner permissions in channel1
    # without test_user promoting their channel permission, proving their global permissions
    # have been updated
    owners1 = channel.channel_details(test_dict['token'], channel1_id)['owner_members']
    assert len(owners1) == 2

    # Checks that another_user automatically gets channel owner permissions upon
    # joining a new channel, proving their global permissions
    channel.channel_join(another_dict['token'], channel2_id)
    owners2 = channel.channel_details(test_dict['token'], channel2_id)['owner_members']
    assert len(owners2) == 2

    # Tests that demoting a user doesn't raise an error
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 2) == {}

def test_admin_userpermission_change_already_promoted():
    '''Tests the intended uses of the admin_userpermission_change() function'''
    other.clear()

    # Registers 2 users
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    # Promotes another_user twice to ensure that
    # promoting an already promoted user doesn't throw an error
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}

def test_admin_userpermission_change_already_demoted():
    '''Tests the intended uses of the admin_userpermission_change() function'''
    other.clear()

    # Registers 2 users
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    # Promotes the user for demotion
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}

    # Demotes another_user twice, once to actually demote them, and another time to
    # ensure that demoting an already demoted user doesn't throw an error
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 2) == {}
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 2) == {}

def test_admin_userpermission_change_remove_initial():
    '''Tests that the initial user to register cannot have their global owner permissions removed
    in the admin_userpermission_change() function'''
    other.clear()

    # Registers 2 users
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    # Promotes another_user so they can try demoting the initial user, raising an access error
    # as you cannot demote the initial user
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}

    with pytest.raises(AccessError):
        assert other.admin_userpermission_change(another_dict['token'], test_dict['u_id'], 2)

def test_admin_userpermission_change_remove_unauthorised():
    '''Tests that users without global owner permissions can't change
    other users' global permissions in the admin_userpermission_change() function'''
    other.clear()

    # Registers 3 users
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    final_dict = auth.auth_register('final@email.com', 'final_password',
                                    'final_first', 'final_last')

    # Promotes another_user so that final_user can attempt to demote them,
    # raising an access error as final_user does not have global owner permissions
    assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1) == {}

    with pytest.raises(AccessError):
        assert other.admin_userpermission_change(final_dict['token'], another_dict['u_id'], 1)

    # Promotes and then demotes final_user and then final_user attempts to demote another_user,
    # testing whether a user who previously had global owner permissions can use the function
    assert other.admin_userpermission_change(test_dict['token'], final_dict['u_id'], 1) == {}
    assert other.admin_userpermission_change(test_dict['token'], final_dict['u_id'], 2) == {}

    with pytest.raises(AccessError):
        assert other.admin_userpermission_change(final_dict['token'], another_dict['u_id'], 2)

def test_admin_userpermission_change_invalid_user():
    '''Tests that an input error is raised when an invalid u_id is used
    in the admin_userpermission_change() function'''
    other.clear()

    # Registers a user and then tests the function with an invalid u_id
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    with pytest.raises(InputError):
        assert other.admin_userpermission_change(test_dict['token'], -1, 1)
    with pytest.raises(InputError):
        assert other.admin_userpermission_change(test_dict['token'], 0, 1)
    with pytest.raises(InputError):
        assert other.admin_userpermission_change(test_dict['token'], 2, 1)

def test_admin_userpermission_change_invalid_perm():
    '''Tests that an input error is raised when an invalid permission_id is used
    in the admin_userpermission_change() function'''
    other.clear()

    # Registers 2 users and then tests the function with invalid permission_id's
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    with pytest.raises(InputError):
        assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 0)
    with pytest.raises(InputError):
        assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 3)

def test_admin_userpermission_change_invalid_token():
    '''Tests that an access error is raised when an invalid token is used
    in the admin_userpermission_change() function'''
    other.clear()

    # Registers two users and then tests the function with an invalid token
    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    auth.auth_logout(test_dict['token'])

    another_dict = auth.auth_register('another@email.com', 'another_password',
                                      'another_first', 'another_last')

    with pytest.raises(AccessError):
        assert other.admin_userpermission_change('invalid_token', another_dict['u_id'], 1)
    with pytest.raises(AccessError):
        assert other.admin_userpermission_change(test_dict['token'], another_dict['u_id'], 1)

def test_search_empty():
    '''Tests the search function when there are no channels'''
    other.clear()

    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    assert other.search(test_token, 'key')['messages'] == []

def test_search_in_channel_by_user():
    '''Tests that messages posted by the user are returned
    by the search() function'''
    other.clear()

    # Registers a user
    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    # Creates a channel
    channel1_id = channels.channels_create(test_token, 'channel1', True)['channel_id']

    # test_user posts messages in channel1
    message1_id = message.message_send(test_token, channel1_id, 'key')['message_id']
    message2_id = message.message_send(test_token, channel1_id, 'Monkey')['message_id']
    message.message_send(test_token, channel1_id, 'Keyboard')
    message4_id = message.message_send(test_token, channel1_id, 'My keyboard')['message_id']
    message.message_send(test_token, channel1_id, 'Lock')

    # all the message_id's of messages in channels that test_user is in
    # that also contain the string 'key' are put in a list
    message_list = [message1_id, message2_id, message4_id]

    # The search() function is called with the string 'key'. The returned list is checked against
    # the premade list for any unrecorded message_id's
    messages = other.search(test_token, 'key')['messages']

    count = 0

    for msg in messages:
        assert msg['message_id'] in message_list
        count += 1
    assert count == 3

def test_search_in_channel_by_other():
    '''Tests that messages posted by another user are returned
    by the search() function'''
    other.clear()

    # Registers 2 users
    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    another_token = auth.auth_register('another@email.com', 'another_password',
                                       'another_first', 'another_last')['token']

    # Creates a channel
    channel1_id = channels.channels_create(test_token, 'channel1', True)['channel_id']

    # Joins another_user to the first channel
    channel.channel_join(another_token, channel1_id)

    # another_user posts messages in channel1
    message6_id = message.message_send(another_token, channel1_id, 'key')['message_id']
    message7_id = message.message_send(another_token, channel1_id, 'Monkey')['message_id']
    message.message_send(another_token, channel1_id, 'Keyboard')
    message9_id = message.message_send(another_token, channel1_id, 'My keyboard')['message_id']
    message.message_send(another_token, channel1_id, 'Lock')

    # all the message_id's of messages in channels that test_user is in
    # that also contain the string 'key' are put in a list
    message_list = [message6_id, message7_id, message9_id]

    # The search() function is called with the string 'key'. The returned list is checked against
    # the premade list for any unrecorded message_id's
    messages = other.search(test_token, 'key')['messages']

    count = 0

    for msg in messages:
        assert msg['message_id'] in message_list
        count += 1
    assert count == 3

def test_search_not_in_channel_by_other():
    '''Tests that messages in channels the user is not in are not returned
    by the search() function'''
    other.clear()

    # Registers 2 users
    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    another_token = auth.auth_register('another@email.com', 'another_password',
                                       'another_first', 'another_last')['token']

    # Creates a channels
    channel2_id = channels.channels_create(another_token, 'channel2', True)['channel_id']

    # another_user posts messages in channel2
    message.message_send(another_token, channel2_id, 'key')
    message.message_send(another_token, channel2_id, 'Monkey')
    message.message_send(another_token, channel2_id, 'Keyboard')
    message.message_send(another_token, channel2_id, 'My keyboard')
    message.message_send(another_token, channel2_id, 'Lock')

    # The search() function is called with the string 'key'. The returned list is checked against
    # the premade list for any unrecorded message_id's
    messages = other.search(test_token, 'key')['messages']

    assert messages == []

def test_search_invalid_token():
    '''Tests that an access error is raised when
    an invalid token is used in the search() function'''
    other.clear()

    with pytest.raises(AccessError):
        assert other.search('invalid_token', 'key')

    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    auth.auth_logout(test_dict['token'])

    with pytest.raises(AccessError):
        assert other.search(test_dict['token'], 'key')
