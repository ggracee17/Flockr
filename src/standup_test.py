"""
Test standup functions
"""
import time
import pytest
import standup
import auth
import message
import channel
import channels
import error
import other

def test_standup_start():
    '''
    Test simple standup_start
    '''

    other.clear()

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel1", True)
    new_channel1 = channel1['channel_id']
    channel2 = channels.channels_create(token1, "Test_Channel2", True)
    new_channel2 = channel2['channel_id']

    message.message_send(token1, new_channel1, "Hello, this is the first message")
    finish = standup.standup_start(token1, new_channel1, 1)
    assert finish
    standup.standup_send(token1, new_channel1, "Hello, this is the secret message")
    standup.standup_send(token1, new_channel1, "Hello, this is the second secret message")
    time.sleep(1.5)
    active = standup.standup_active(token1, new_channel2)
    assert not active['is_active']

def test_standup_start_invalid_channel_id():
    '''
    Test standup_start channel_id error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']

    with pytest.raises(error.InputError):
        standup.standup_start(token1, new_channel + 45, 1)

def test_standup_start_error_token():
    '''
    Test standup_start token error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(error.AccessError):
        assert standup.standup_start(token2, new_channel, 1)

def test_standup_start_invalid_user():
    '''
    Test standup_start token error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(error.AccessError):
        assert standup.standup_start(token2 + 'az', new_channel, 1)

def test_standup_start_error_already_running_same_user():
    '''
    Test standup_start already running error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.InputError):
        assert standup.standup_start(token1, new_channel, 1)

def test_standup_start_error_already_running_different_user():
    '''
    Test standup_start already running by another user error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.InputError):
        assert standup.standup_start(token2, new_channel, 1)

def test_standup_active():
    '''
    Test simple standup_active
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    active = standup.standup_active(token1, new_channel)
    assert active


def test_standup_active_error_channel_id():
    '''
    Test standup_active channel_id error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.InputError):
        assert standup.standup_active(token1, new_channel + 45)

def test_standup_active_error_token():
    '''
    Test standup_active token error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.AccessError):
        assert standup.standup_active(token2, new_channel)

def test_standup_send():
    '''
    Test simple standup_send
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']
    u_id2 = user2['u_id']

    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    channel.channel_invite(token1, new_channel, u_id2)

    message.message_send(token1, new_channel, "Hello, this is the first message")
    finish = standup.standup_start(token1, new_channel, 1)
    message.message_send(token2, new_channel, "Hello, this is the second message")
    assert finish
    standup.standup_send(token1, new_channel, "Hi, this is a standup session")


def test_standup_send_error_no_session():
    '''
    Test standup_active no session error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel2 = channels.channels_create(token1, "Test_Channel2", True)
    new_channel2 = channel2['channel_id']

    with pytest.raises(error.InputError):
        assert standup.standup_send(token1, new_channel2, "This is an error!")

def test_standup_send_error_active_session():
    '''
    Test standup_active no session error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel2 = channels.channels_create(token1, "Test_Channel2", True)
    new_channel2 = channel2['channel_id']

    standup.standup_start(token1, new_channel2, 1)
    with pytest.raises(error.InputError):
        assert standup.standup_send(token1, new_channel2, "/standup 20")

def test_standup_send_error_channel_id():
    '''
    Test standup_send no standup session error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    with pytest.raises(error.InputError):
        standup.standup_send(token1, new_channel + 45, "Hi, this is a standup session")

def test_standup_send_error_long_message():
    '''
    Test standup_send long message error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    u_id2 = user2['u_id']
    channel.channel_invite(token1, new_channel, u_id2)

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.InputError):
        standup.standup_send(token1, new_channel, \
        '''
        Hi, this is a standup session
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
        ''')

def test_standup_send_error_access():
    '''
    Test standup_send access error
    '''

    other.clear()
    time.sleep(2)

    #Creates new user and channel
    user1 = auth.auth_register("user1@email.com", "password1", "First1", "Last1")
    token1 = user1['token']
    channel1 = channels.channels_create(token1, "Test_Channel", True)
    new_channel = channel1['channel_id']
    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    finish = standup.standup_start(token1, new_channel, 1)
    assert finish
    with pytest.raises(error.AccessError):
        standup.standup_send(token2, new_channel, "Hi this is a standup message")
