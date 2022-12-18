'''
Tests for message_send(token, channel_id, message),
message_remove(token, message_id), and
message_edit(token, message_id, message)
'''

import datetime
import pytest
import other
import channel
import auth
import channels
import message
import error

REACT_ID = 1
INVALID_REACT_ID = -1
INVALID_M_ID = 99

def test_send_messages():
    '''
    Tests for valid messages
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    message1 = 'Hello World'
    message2 = 'Goodbye'
    message3 = 'Happy Birthday'

    # send one message to channel1
    assert message.message_send(token1, c_id1, message1) == {'message_id': 1}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert messages['start'] == 0
    assert messages['end'] == -1
    assert len(messages['messages']) == 1
    msg = messages['messages'][0]
    assert msg['message_id'] == 1
    assert msg['u_id'] == user1['u_id']
    assert msg['message'] == message1

    # send another message to channel1
    assert message.message_send(token1, c_id1, message2) == {'message_id': 2}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 2
    msg0 = messages['messages'][0]
    assert msg0['message_id'] == 2
    assert msg0['u_id'] == user1['u_id']
    assert msg0['message'] == message2
    msg1 = messages['messages'][1]
    assert msg1['message_id'] == 1
    assert msg1['u_id'] == user1['u_id']
    assert msg1['message'] == message1

    # send one message to channel2
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']
    assert message.message_send(token2, c_id2, message3) == {'message_id': 3}
    messages = channel.channel_messages(token2, c_id2, 0)
    assert len(messages['messages']) == 1
    msg = messages['messages'][0]
    assert msg['message_id'] == 3
    assert msg['u_id'] == user2['u_id']
    assert msg['message'] == message3

def test_very_long_message():
    '''
    Test input error of message that is more than 1000 chatacters long
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # create a message with more than 1000 characters
    long_string = 'x' * 1001
    with pytest.raises(error.InputError):
        message.message_send(token1, c_id1, long_string)

    msg = message.message_send(token1, c_id1, 'Hello World')
    with pytest.raises(error.InputError):
        message.message_edit(token1, msg['message_id'], long_string)

def test_unordered_message_id():
    '''
    Tests for when message_ids in channels are not in order
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']
    message1 = 'Hello World'
    message2 = 'Goodbye'
    message3 = 'Happy Birthday'

    # send messages to channel2 first
    message.message_send(token2, c_id2, message3)
    message.message_send(token2, c_id2, message1)
    message.message_send(token2, c_id2, message2)
    messages = channel.channel_messages(token2, c_id2, 0)
    assert len(messages['messages']) == 3
    msg0 = messages['messages'][0]
    assert msg0['message_id'] == 3
    assert msg0['u_id'] == user2['u_id']
    assert msg0['message'] == message2
    msg1 = messages['messages'][1]
    assert msg1['message_id'] == 2
    assert msg1['u_id'] == user2['u_id']
    assert msg1['message'] == message1
    msg2 = messages['messages'][2]
    assert msg2['message_id'] == 1
    assert msg2['u_id'] == user2['u_id']
    assert msg2['message'] == message3

    # then send messages to channel1
    message.message_send(token1, c_id1, message2)
    message.message_send(token1, c_id1, message1)
    message.message_send(token1, c_id1, message3)
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 3
    msg0 = messages['messages'][0]
    assert msg0['message_id'] == 6
    assert msg0['u_id'] == user1['u_id']
    assert msg0['message'] == message3
    msg1 = messages['messages'][1]
    assert msg1['message_id'] == 5
    assert msg1['u_id'] == user1['u_id']
    assert msg1['message'] == message1
    msg2 = messages['messages'][2]
    assert msg2['message_id'] == 4
    assert msg2['u_id'] == user1['u_id']
    assert msg2['message'] == message2


def test_send_invalid_access():
    '''
    Tests for when the authorised user has not joined the channel
    they are trying to post to, or when no channels has been created
    '''
    other.clear()
    user1, user2 = add_user_info()
    message1 = 'Hello World'

    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], 1, message1)
    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], 0, message1)
    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], -1, message1)
    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], 99, message1)

    channel1 = channels.channels_create(user1['token'], 'channel1', True)
    channel2 = channels.channels_create(user2['token'], 'channel2', True)
    c_id1 = channel1['channel_id']
    c_id2 = channel2['channel_id']

    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], c_id2, message1)
    with pytest.raises(error.AccessError):
        message.message_send(user2['token'], c_id1, message1)
    with pytest.raises(error.AccessError):
        message.message_send(user1['token'], 3, message1)

def test_remove_messages():
    '''
    Tests for removing messages
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']

    # send three messages to channel1
    message.message_send(token1, c_id1, 'Hello World')
    msg2 = message.message_send(token1, c_id1, 'Goodbye')
    m_id2 = msg2['message_id']
    message.message_send(token1, c_id1, 'Happy Birthday')
    assert len(channel.channel_messages(token1, c_id1, 0)['messages']) == 3

    # remove the second message
    message.message_remove(token1, m_id2)
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 2
    msg0 = messages['messages'][0]
    assert msg0['message_id'] == 3
    assert msg0['u_id'] == user1['u_id']
    assert msg0['message'] == 'Happy Birthday'
    msg1 = messages['messages'][1]
    assert msg1['message_id'] == 1
    assert msg1['u_id'] == user1['u_id']
    assert msg1['message'] == 'Hello World'

    # send two messages to channel2
    msg4 = message.message_send(token2, c_id2, 'Merry Christmans')
    m_id4 = msg4['message_id']
    message.message_send(token2, c_id2, 'Iteration 1: Basic functionality and tests')
    assert len(channel.channel_messages(token1, c_id1, 0)['messages']) == 2
    assert len(channel.channel_messages(token2, c_id2, 0)['messages']) == 2

    # remove the first message in channel2
    message.message_remove(token2, m_id4)
    assert len(channel.channel_messages(token1, c_id1, 0)['messages']) == 2
    assert len(channel.channel_messages(token2, c_id2, 0)['messages']) == 1

    with pytest.raises(error.InputError):
        message.message_remove(token2, m_id4)
    with pytest.raises(error.InputError):
        message.message_remove(token1, m_id2)

def test_invalid_message_id():
    '''
    Function for testing invalid message ids
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    with pytest.raises(error.InputError):
        message.message_remove(token1, 1)
    with pytest.raises(error.InputError):
        message.message_remove(token1, 2)

    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    message.message_send(token1, c_id1, 'Hello World')
    with pytest.raises(error.InputError):
        message.message_remove(token1, 99)
    with pytest.raises(error.InputError):
        message.message_remove(token1, 0)
    with pytest.raises(error.InputError):
        message.message_remove(token2, -1)

def test_remove_invalid_access():
    '''
    Function for testing invalid user access for removing messages
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    u_id2 = user2['u_id']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    assert channel.channel_messages(token1, c_id1, 0)['messages'] == []

    # invite user2 to join channel1, user2 send a message to channel1
    channel.channel_invite(token1, c_id1, u_id2)
    message1 = message.message_send(token2, c_id1, 'Hello World')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1

    # user2 remove the message sent in channel1
    message.message_remove(token2, message1['message_id'])
    assert channel.channel_messages(token1, c_id1, 0)['messages'] == []

    # user2 send another message to channel1
    message2 = message.message_send(token2, c_id1, 'Hi there again')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1

    # user1 remove the message sent by user2 in channel1
    message.message_remove(token1, message2['message_id'])
    assert channel.channel_messages(token1, c_id1, 0)['messages'] == []

    # invite user3 into channel1
    user3 = auth.auth_register('final@email.com', 'final_password', 'Sam', 'Smith')
    user3 = auth.auth_login('final@email.com', 'final_password')
    token3 = user3['token']
    channel.channel_invite(token1, c_id1, user3['u_id'])

    # user3 cannot remove messages sent by user1 or user2
    message3 = message.message_send(token1, c_id1, 'I am user1')
    message4 = message.message_send(token2, c_id1, 'I am user2')
    with pytest.raises(error.AccessError):
        message.message_remove(token3, message3['message_id'])
    with pytest.raises(error.AccessError):
        message.message_remove(token3, message4['message_id'])

def test_edit_message():
    '''
    Tests for editing messages
    '''
    other.clear()
    # create user and channel
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # send messages to the channel
    message1 = message.message_send(token1, c_id1, 'Hello World')
    message2 = message.message_send(token1, c_id1, 'Hi there again')
    message3 = message.message_send(token1, c_id1, 'I am user1')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 3

    # edit message1
    message.message_edit(token1, message1['message_id'], 'How are you')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 3
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'I am user1'
    msg1 = messages['messages'][1]
    assert msg1['message'] == 'Hi there again'
    msg2 = messages['messages'][2]
    assert msg2['message'] == 'How are you'

    # edit message3
    message.message_edit(token1, message3['message_id'], 'Guess who am I')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 3
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'Guess who am I'
    msg1 = messages['messages'][1]
    assert msg1['message'] == 'Hi there again'
    msg2 = messages['messages'][2]
    assert msg2['message'] == 'How are you'

    # delete message2
    message.message_edit(token1, message2['message_id'], '')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 2
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'Guess who am I'
    msg1 = messages['messages'][1]
    assert msg1['message'] == 'How are you'

    #delete message1
    message.message_edit(token1, message1['message_id'], '')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'Guess who am I'

def test_edit_invalid_access():
    '''
    Function for testing invalid user access for editing messages
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # invite user2 to join channel1, user2 send a message to channel1
    channel.channel_invite(token1, c_id1, user2['u_id'])
    message1 = message.message_send(token2, c_id1, 'Hello World')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1

    # user2 edit the message sent in channel1
    message.message_edit(token2, message1['message_id'], 'Hello Universe')
    messages = channel.channel_messages(token2, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'Hello Universe'

    # user2 send another message to channel1
    message2 = message.message_send(token2, c_id1, 'Hi there again')
    messages = channel.channel_messages(token2, c_id1, 0)
    assert len(messages['messages']) == 2

    # user1 edit the message sent by user2 in channel1
    message.message_edit(token1, message2['message_id'], 'Welcome to my channel')
    messages = channel.channel_messages(token2, c_id1, 0)
    assert len(messages['messages']) == 2
    msg0 = messages['messages'][0]
    assert msg0['message'] == 'Welcome to my channel'
    msg1 = messages['messages'][1]
    assert msg1['message'] == 'Hello Universe'

    # invite user3 into channel1
    user3 = auth.auth_register('final@email.com', 'final_password', 'Sam', 'Smith')
    token3 = user3['token']
    channel.channel_invite(token1, c_id1, user3['u_id'])

    # user3 cannot edit messages sent by user1 or user2
    message3 = message.message_send(token1, c_id1, 'I am user1')
    message4 = message.message_send(token2, c_id1, 'I am user2')
    with pytest.raises(error.AccessError):
        message.message_edit(token3, message3['message_id'], 'I am user3')
    with pytest.raises(error.AccessError):
        message.message_edit(token3, message4['message_id'], 'I am user3')

    # user1 removes all messages
    message.message_edit(token1, message1['message_id'], '')
    message.message_edit(token1, message2['message_id'], '')
    message.message_edit(token1, message3['message_id'], '')
    message.message_edit(token1, message4['message_id'], '')
    assert channel.channel_messages(token1, c_id1, 0)['messages'] == []

def test_valid_sendlater():
    '''
    Tests valid inputs for the sendlater function
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # user1 sends a message to channel1 2 secs and 3 secs later
    now = datetime.datetime.now()
    two_sec_later = now + datetime.timedelta(seconds=2)
    three_sec_later = now + datetime.timedelta(seconds=3)
    time_sent2 = two_sec_later.timestamp()
    time_sent3 = three_sec_later.timestamp()

    # check that return value is correct
    result1 = message.message_sendlater(token1, c_id1, 'Hello', time_sent3)
    result2 = message.message_sendlater(token1, c_id1, 'Hello', time_sent2)
    assert 'message_id' in result1 and 'message_id' in result2

    # check that the messages are not in the channel yet
    assert channel.channel_messages(token1, c_id1, 0)['messages'] == []

def test_sendlater_input_error():
    '''
    Test invalid channel_id, invalid length of message and invalid time_sent
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    invalid_c_id = 99

    # send a message with invalid channel_id
    now = datetime.datetime.now()
    two_sec_later = now + datetime.timedelta(seconds=2)
    time_sent = two_sec_later.timestamp()
    with pytest.raises(error.InputError):
        message.message_sendlater(token1, invalid_c_id, 'Hello', time_sent)

    # send a message with invalid length
    long_string = 'x' * 1001
    with pytest.raises(error.InputError):
        message.message_sendlater(token1, c_id1, long_string, time_sent)

    # send a message with invalid send time
    now = datetime.datetime.now()
    ten_sec_ago = now - datetime.timedelta(seconds=10)
    time_sent = ten_sec_ago.timestamp()
    with pytest.raises(error.InputError):
        message.message_sendlater(token1, c_id1, 'Hello', time_sent)

def test_sendlater_access_error():
    '''
    Test when user has not joined the channel they are trying to post to
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # user2 tries to send message to channel1
    now = datetime.datetime.now()
    two_sec_later = now + datetime.timedelta(seconds=2)
    time_sent = two_sec_later.timestamp()
    with pytest.raises(error.AccessError):
        message.message_sendlater(token2, c_id1, 'Hello', time_sent)

def test_valid_pin():
    '''
    Test valid inputs for message_pin and message_unpin function
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # send one message to channel1, check message sent successfully
    message1 = message.message_send(token1, c_id1, 'Hello World')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert not msg0['is_pinned']

    # pin the message, check that function returns an empty list
    assert message.message_pin(token1, message1['message_id']) == {}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert msg0['is_pinned']

    assert message.message_unpin(token1, message1['message_id']) == {}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert not msg0['is_pinned']

def test_pin_input_error():
    '''
    Test invalid message_id and already pinned/unpinned messages
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    token1 = user1['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # user1 send one message to channel1
    message1 = message.message_send(token1, c_id1, 'Hello World')

    # check that message is already unpinned
    with pytest.raises(error.InputError):
        message.message_unpin(token1, message1['message_id'])

    # test pin and unpin with invalid message_id
    with pytest.raises(error.InputError):
        message.message_pin(token1, INVALID_M_ID)
    with pytest.raises(error.InputError):
        message.message_unpin(token1, INVALID_M_ID)

    # pin the message, check that message is already pinned
    message.message_pin(token1, message1['message_id'])
    with pytest.raises(error.InputError):
        message.message_pin(token1, message1['message_id'])

def test_pin_access_error():
    '''
    Test when user is not a member of the channel,
    or when user is not an owner,
    or when an invalid token is passed in
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    channels.channels_create(token1, 'channel2', True)
    c_id1 = channel1['channel_id']
    invalid_token = 'random_token'

    # user1 send a message to channel1
    message1 = message.message_send(token1, c_id1, 'Hello World')

    # check that an invalid token raises an access error
    with pytest.raises(error.AccessError):
        message.message_pin(invalid_token, message1['message_id'])
    with pytest.raises(error.AccessError):
        message.message_unpin(invalid_token, message1['message_id'])

    # check user2 cannot pin/unpin the message
    # until he is added to channel and added as an owner
    with pytest.raises(error.AccessError):
        message.message_pin(token2, message1['message_id'])

    message.message_pin(token1, message1['message_id'])
    with pytest.raises(error.AccessError):
        message.message_unpin(token2, message1['message_id'])
    message.message_unpin(token1, message1['message_id'])

    # user1 invite user2 to join channel1
    channel.channel_invite(token1, c_id1, user2['u_id'])
    with pytest.raises(error.AccessError):
        message.message_pin(token2, message1['message_id'])

    message.message_pin(token1, message1['message_id'])
    with pytest.raises(error.AccessError):
        message.message_unpin(token2, message1['message_id'])
    message.message_unpin(token1, message1['message_id'])

    # user1 make user2 an owner of channel1
    channel.channel_addowner(token1, c_id1, user2['u_id'])
    assert message.message_pin(token2, message1['message_id']) == {}
    assert message.message_unpin(token2, message1['message_id']) == {}

def test_valid_react():
    '''
    Test valid inputs for message_react and message_unreact functions
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']

    # user1 invites user2 to join channel1
    channel.channel_invite(token1, c_id1, user2['u_id'])

    # user1 send one message to channel1
    message1 = message.message_send(token1, c_id1, 'Hello World')
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert 'reacts' in msg0
    assert not msg0['reacts']

    # user1 react to the message
    assert message.message_react(token1, message1['message_id'], REACT_ID) == {}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    rct0 = msg0['reacts'][0]
    assert rct0['react_id'] == 1
    assert rct0['u_ids'] == [user1['u_id']]
    assert rct0['is_this_user_reacted']

    # check that user2 has not reacted to the message
    messages = channel.channel_messages(token2, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    rct0 = msg0['reacts'][0]
    assert rct0['react_id'] == 1
    assert rct0['u_ids'] == [user1['u_id']]
    assert not rct0['is_this_user_reacted']

    # check 'is_this_user_reacted' key in search function
    messages = other.search(token1, 'Hello')
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    rct0 = msg0['reacts'][0]
    assert rct0['react_id'] == 1
    assert rct0['u_ids'] == [user1['u_id']]
    assert rct0['is_this_user_reacted']

    messages = other.search(token2, 'Hello')
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    rct0 = msg0['reacts'][0]
    assert rct0['react_id'] == 1
    assert rct0['u_ids'] == [user1['u_id']]
    assert not rct0['is_this_user_reacted']

    # user1 unreact the message
    assert message.message_unreact(token1, message1['message_id'], REACT_ID) == {}
    messages = channel.channel_messages(token1, c_id1, 0)
    assert len(messages['messages']) == 1
    msg0 = messages['messages'][0]
    assert not msg0['reacts']

def test_react_multiple_channels():
    '''
    Test valid reacts/unreacts of when user is in multiple channels
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    channel2 = channels.channels_create(token1, 'channel2', True)

    # user1 invites user2 to join channel2
    channel.channel_invite(token1, channel2['channel_id'], user2['u_id'])

    # user1 send messages to each of channel1 and channel2
    message1 = message.message_send(token1, channel1['channel_id'], 'Hello Channel1')
    message2 = message.message_send(token1, channel2['channel_id'], 'Hello Channel2')
    message3 = message.message_send(token1, channel2['channel_id'], 'How r u')

    # user1 react to message2, user2 react to message2 and 3
    assert message.message_react(token1, message2['message_id'], REACT_ID) == {}
    assert message.message_react(token2, message2['message_id'], REACT_ID) == {}
    assert message.message_react(token2, message3['message_id'], REACT_ID) == {}

    # user1 cannot unreact message3
    with pytest.raises(error.InputError):
        message.message_unreact(token1, message3['message_id'], REACT_ID)

    # user2 cannot react to message1, user2 cannot react to message3 again
    with pytest.raises(error.InputError):
        message.message_react(token2, message1['message_id'], REACT_ID)
    with pytest.raises(error.InputError):
        message.message_react(token2, message3['message_id'], REACT_ID)

    # user2 unreact message3, user1 unreact message2
    assert message.message_unreact(token1, message2['message_id'], REACT_ID) == {}
    assert message.message_unreact(token2, message3['message_id'], REACT_ID) == {}

    # user2 cannot unreact message1, user2 cannot unreact message3 again
    with pytest.raises(error.InputError):
        message.message_unreact(token2, message1['message_id'], REACT_ID)
    with pytest.raises(error.InputError):
        message.message_unreact(token2, message3['message_id'], REACT_ID)

def test_react_input_error():
    '''
    Test invalid message_id, react_id and already reacted/unreacted messages
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    channel1 = channels.channels_create(token1, 'channel1', True)
    c_id1 = channel1['channel_id']
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']

    # user1 send one message to channel1, user2 send one message to channel2
    message1 = message.message_send(token1, c_id1, 'Hello Channel1')
    message2 = message.message_send(token2, c_id2, 'Hello Channel2')

    # test message_id that does not exist
    with pytest.raises(error.InputError):
        message.message_react(token1, INVALID_M_ID, REACT_ID)
    with pytest.raises(error.InputError):
        message.message_unreact(token1, INVALID_M_ID, REACT_ID)

    # test message_id in a channel not joined
    with pytest.raises(error.InputError):
        message.message_react(token1, message2['message_id'], REACT_ID)
    with pytest.raises(error.InputError):
        message.message_unreact(token1, message2['message_id'], REACT_ID)

    # test invalid react_id
    with pytest.raises(error.InputError):
        message.message_react(token1, message1['message_id'], INVALID_REACT_ID)
    with pytest.raises(error.InputError):
        message.message_unreact(token1, message1['message_id'], INVALID_REACT_ID)

    # test already unreacted/reacted message
    with pytest.raises(error.InputError):
        message.message_unreact(token1, message1['message_id'], REACT_ID)
    message.message_react(token1, message1['message_id'], REACT_ID)
    with pytest.raises(error.InputError):
        message.message_react(token1, message1['message_id'], REACT_ID)
    assert message.message_unreact(token1, message1['message_id'], REACT_ID) == {}
    with pytest.raises(error.InputError):
        message.message_unreact(token1, message1['message_id'], REACT_ID)

def test_check_owner():
    '''
    Tests for the check_owner helper function
    '''
    other.clear()
    user1, user2 = add_user_info()
    token1 = user1['token']
    token2 = user2['token']
    user3 = auth.auth_register('final@email.com', 'final_password', 'Sam', 'Smith')
    token3 = user3['token']
    u_id3 = user3['u_id']

    channels.channels_create(token1, 'channel1', True)
    channel2 = channels.channels_create(token2, 'channel2', True)
    c_id2 = channel2['channel_id']

    msg = message.message_send(token2, c_id2, 'Hello World')

    # user2 invite user3 into channel2, user3 try to remove messages
    channel.channel_invite(token2, c_id2, u_id3)
    with pytest.raises(error.AccessError):
        message.message_remove(token3, msg['message_id'])

    # user2 add user3 as an owner of channel2, then user3 can remove messages
    channel.channel_addowner(token2, c_id2, u_id3)
    message.message_remove(token3, msg['message_id'])
    assert channel.channel_messages(token2, c_id2, 0)['messages'] == []

def add_user_info():
    '''
    Function to register and login two users for testing purpose
    '''
    user1 = auth.auth_register('test@email.com', 'test_password', 'Hayden', 'Jacobs')
    user2 = auth.auth_register('another@email.com', 'another_password', 'Sam', 'Smith')
    return user1, user2
