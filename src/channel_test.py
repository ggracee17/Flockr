"""
Tests for channel_leave, channel_join, channel_addowner, channel_removeowner
"""

import pytest
import auth
import channel
import channels
import error
import other
import data

def test_channel_empty_leave():
    '''
    Test channel_leave works with no created channels
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(error.InputError):
        assert channel.channel_leave(token1, 1)

def test_channel_leave():
    '''
    Test channel_leave
    '''
    other.clear()

    #Test that a member has left the channel
    #Creates new user and channel
    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)
    #Check if channel_leave is success
    channel.channel_leave(token2, new_channel)

    u_id_list = []
    for chan in data.channels:
        if chan['channel_id'] == new_channel:
            for member in chan['all_members']:
                u_id_list.append(member['u_id'])

    assert u_id2 not in u_id_list

def test_channel_ownerleave():
    '''
    Test owner leaving channel
    '''
    #Reset application
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    channel.channel_leave(token1, new_channel)
    assert not data.channels

    #recreate 2 channels
    channels.channels_create(token1, "Another_Channel", True)
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']

    #register user2, add user2 as owner of channel1 then user1 leaves channel
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    channel.channel_addowner(token1, new_channel, user2['u_id'])
    channel.channel_leave(token1, new_channel)
    u_id_list = []
    for chan in data.channels:
        if chan['channel_id'] == new_channel:
            for member in chan['all_members']:
                u_id_list.append(member['u_id'])

    assert user1['u_id'] not in u_id_list

    #last owner user2 leaves channel1
    channel.channel_leave(user2['token'], new_channel)
    assert len(data.channels) == 1

def test_channel_leave_inputerror():
    '''
    Test channel_leave with input error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First", "Last")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    with pytest.raises(error.InputError):
        assert channel.channel_leave(token1, (new_channel + 45))

def test_channel_leave_accesserror():
    '''
    Test channel_leave with access error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    assert channels.channels_list(token1)

    with pytest.raises(error.AccessError):
        assert channel.channel_leave(token2, new_channel)

def test_channel_empty_join():
    '''
    Test channel_join with no channels created
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(error.InputError):
        assert channel.channel_join(token1, 1)

def test_channel_join():
    '''
    Test channel_join
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    channel.channel_join(token2, new_channel)
    assert channels.channels_list(token2)

def test_channel_join_global_owner():
    '''
    Test channel_join automatically promotes global owners to channel owners
    '''
    other.clear()

    #Creates new users and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token1 = user1['token']
    token2 = user2['token']
    u_id2 = user2['u_id']
    other.admin_userpermission_change(token1, u_id2, 1)

    #Adds global owner to channel
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    channel.channel_join(token2, new_channel)

    is_owner = False

    #Checks global owner is channel owner
    owners = channel.channel_details(token1, new_channel)['owner_members']
    for owner in owners:
        if owner['u_id'] == u_id2:
            is_owner = True

    assert is_owner

def test_channel_join_inputerror():
    '''
    Test channel_join with input error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    with pytest.raises(error.InputError):
        assert channel.channel_join(token2, (new_channel + 45))

def test_channel_join_accesserror():
    '''
    Test channel_join wih access error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", False)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    with pytest.raises(error.AccessError):
        assert channel.channel_join(token2, new_channel)

def test_channel_addowner():
    '''
    Test channel_addowner
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']
    channel.channel_addowner(token1, new_channel, u_id2)
    channel_detail = channel.channel_details(token2, new_channel)

    res = False
    for owner in channel_detail['owner_members']:
        if owner['u_id'] == u_id2:
            res = True

    assert res

def test_channel_addowner_inputerror_invalid_id():
    '''
    Test channel_addowner input error with invalid channel_id
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    with pytest.raises(error.InputError):
        channel.channel_addowner(token1, new_channel + 45, u_id2)

    other.clear()

def test_channel_addowner_inputerror_existing():
    '''
    Test channel_addowner input error with already an owner
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    u_id1 = user1['u_id']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']
    channel.channel_addowner(token1, new_channel, u_id2)

    with pytest.raises(error.InputError):
        channel.channel_addowner(token1, new_channel, u_id2)
    with pytest.raises(error.InputError):
        channel.channel_addowner(token1, new_channel, u_id1)
    with pytest.raises(error.InputError):
        channel.channel_addowner(token2, new_channel, u_id2)

def test_channel_addowner_accesserror():
    '''
    Test channel_addowner access error with invalid owner token
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']

    user3 = auth.auth_register("user3@email.com", "password3", "First3", "Last3")
    token3 = user3['token']
    u_id3 = user3['u_id']

    with pytest.raises(error.AccessError):
        channel.channel_addowner(token2, new_channel, u_id3)
    with pytest.raises(error.AccessError):
        channel.channel_addowner(token3, new_channel, u_id2)

def test_channel_removeowner():
    '''
    Test channel_removeowner
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']

    channels.channels_create(token1, "Another_Channel", True)
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']

    channel.channel_addowner(token1, new_channel, u_id2)
    channel_detail = channel.channel_details(token2, new_channel)

    res = False
    for owner in channel_detail['owner_members']:
        if owner['u_id'] == u_id2:
            res = True

    assert res

    channel.channel_removeowner(token1, new_channel, u_id2)
    channel_detail = channel.channel_details(token2, new_channel)
    owner_list = []
    for owner in channel_detail['owner_members']:
        owner_list.append(owner['u_id'])

    assert u_id2 not in owner_list

def test_channel_removeowner_last_owner():
    '''
    Test channel_removeowner last owner, channel is deleted
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    channel.channel_leave(token1, new_channel)

    assert data.channels == []

def test_channel_removeowner_global_owner():
    '''
    Test channel_removeowner global owner, raises access error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    user2 = auth.auth_register("user2@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    token2 = user2['token']
    u_id2 = user2['u_id']

    other.admin_userpermission_change(token1, u_id2, 1)
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']

    channel.channel_join(token2, new_channel)

    with pytest.raises(error.AccessError):
        assert channel.channel_removeowner(token1, new_channel, u_id2)


def test_channel_removeowner_inputerror():
    '''
    Test channel_removeowner input error with invalid channel_id
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_addowner(token1, new_channel, u_id2)

    with pytest.raises(error.InputError):
        channel.channel_removeowner(token1, new_channel + 45, \
          u_id2)

def test_channel_removeowner_inputerror2():
    '''
    Test channel_removeowner input error with non-owner member
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']

    with pytest.raises(error.InputError):
        channel.channel_removeowner(token1, new_channel, \
          u_id2)

def test_channel_removeowner_accesserror():
    '''
    Test channel_removeowner access error
    '''
    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    assert channels.channels_list(token1)

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']

    user3 = auth.auth_register("user3@email.com", "password3", "First3", "Last3")
    token3 = user3['token']
    u_id3 = user3['u_id']

    with pytest.raises(error.AccessError):
        channel.channel_removeowner(token2, new_channel, \
          u_id3)
    with pytest.raises(error.AccessError):
        channel.channel_removeowner(token3, new_channel, \
          u_id2)

def test_find_user_error():
    '''
    Test find_user and find_user_u_id input and access error
    '''
    other.clear()
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    invalid_token = 123
    invalid_channel_id = 2
    invalid_u_id = 10
    with pytest.raises(error.InputError):
        channel.channel_join(token1, invalid_channel_id)
    with pytest.raises(error.AccessError):
        channel.channel_join(invalid_token, new_channel)
    with pytest.raises(error.InputError):
        channel.channel_addowner(token1, new_channel, invalid_u_id)
