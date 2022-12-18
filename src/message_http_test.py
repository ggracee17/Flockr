'''
Tests the channel_messages, message_send, message_remove and
message_edit functions in the server
'''

import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import datetime
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

def test_messages(url):
    '''Tests the calling of channel_messages and message functions'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data1)
    assert response.status_code == 200
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data1)
    assert response.status_code == 200
    channel1 = response.json()
    assert 'channel_id' in channel1

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message1 = response.json()
    assert 'message_id' in message1

    # user1 sends another message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good evening'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message2 = response.json()
    assert 'message_id' in message2

    # check that there are 2 messages in channel1
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert 'messages' in msgs
    assert 'start' in msgs
    assert 'end' in msgs
    assert len(msgs['messages']) == 2

    # user1 edit the previous message
    edit_data = {
        'token': user1['token'],
        'message_id': message2['message_id'],
        'message': 'Good night'
    }
    response = requests.put(url + 'message/edit', json=edit_data)
    assert response.status_code == 200
    assert not response.json()

    # check that the most recent message has been changed
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs['messages']) == 2
    assert msgs['messages'][0]['message'] == 'Good night'

    # user1 remove the previous message using edit
    edit_data = {
        'token': user1['token'],
        'message_id': message2['message_id'],
        'message': ''
    }
    response = requests.put(url + 'message/edit', json=edit_data)
    assert response.status_code == 200

    # check that there is only 1 message in channel1
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs['messages']) == 1

    # user1 sends another message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message3 = response.json()
    assert 'message_id' in message3

    # user1 remove the previous message using remove
    rm_data = {
        'token': user1['token'],
        'message_id': message3['message_id'],
    }
    response = requests.delete(url + 'message/remove', json=rm_data)
    assert response.status_code == 200
    assert not response.json()

    # check that there is 1 message in channel1
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs['messages']) == 1

def test_messages_invalid_inputs(url):
    '''Tests the calling of channel_messages
     and message functions with invalid inputs'''
    # register and login user1 and user2
    reg_data = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user1 = response.json()

    reg_data = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user2 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data1)
    assert response.status_code == 200
    channel1 = response.json()
    assert 'channel_id' in channel1

    # test message with invalid length
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'x' * 1010,
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 400

    # test message send with invalid token
    msg_data = {
        'token': INVALID_TOKEN,
        'channel_id': channel1['channel_id'],
        'message': 'Hello',
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 400

    # user2 cannot send a message to channel1
    msg_data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 400

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message1 = response.json()
    assert 'message_id' in message1

    # user1 sends another message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good evening'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message2 = response.json()
    assert 'message_id' in message2

    # check that there are 2 messages in channel1
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert len(msgs['messages']) == 2

    # check message with start at 2
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 2
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200

    # check message with invalid channel id
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'] + 10,
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 400

    # check message with invalid start
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 3
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 400

    # check message with invalid token
    msgs_input = {
        'token': INVALID_TOKEN,
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 400

    # user2 cannot check message of channel1
    msgs_input = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 400

def test_edit_messages_invalid_inputs(url):
    '''Tests the calling of message edit
     and remove functions with invalid inputs'''
    # register and login user1 and user2
    reg_data = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user1 = response.json()

    reg_data = {
        'email': 'another@email.com',
        'password': 'another_pass',
        'name_first': 'another_first',
        'name_last': 'another_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data)
    assert response.status_code == 200
    user2 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data1)
    assert response.status_code == 200
    channel1 = response.json()
    assert 'channel_id' in channel1

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message1 = response.json()
    assert 'message_id' in message1

    # user1 sends another message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good evening'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message2 = response.json()
    assert 'message_id' in message2

    # user2 join channel1
    join_data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
    }
    response = requests.post(url + 'channel/join', json=join_data)
    assert response.status_code == 200

    # user2 cannot edit previous message
    edit_data = {
        'token': user2['token'],
        'message_id': message2['message_id'],
        'message': 'Good evening'
    }
    response = requests.put(url + 'message/edit', json=edit_data)
    assert response.status_code == 400

    # test edit with invalid token
    edit_data = {
        'token': INVALID_TOKEN,
        'message_id': message2['message_id'],
        'message': 'Good evening'
    }
    response = requests.put(url + 'message/edit', json=edit_data)
    assert response.status_code == 400

    # user1 remove the previous message using edit
    edit_data = {
        'token': user1['token'],
        'message_id': message2['message_id'],
        'message': ''
    }
    response = requests.put(url + 'message/edit', json=edit_data)
    assert response.status_code == 200

    # user1 sends another message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning'
    }
    response = requests.post(url + 'message/send', json=msg_data)
    assert response.status_code == 200
    message3 = response.json()
    assert 'message_id' in message3

    # test remove with invalid token
    rm_data = {
        'token': INVALID_TOKEN,
        'message_id': message3['message_id'],
    }
    response = requests.delete(url + 'message/remove', json=rm_data)
    assert response.status_code == 400

    # user1 remove the previous message using remove
    rm_data = {
        'token': user1['token'],
        'message_id': message3['message_id'],
    }
    response = requests.delete(url + 'message/remove', json=rm_data)
    assert response.status_code == 200
    assert not response.json()

    # user2 cannot remove message1
    rm_data = {
        'token': user2['token'],
        'message_id': message1['message_id'],
    }
    response = requests.delete(url + 'message/remove', json=rm_data)
    assert response.status_code == 400

    # user1 cannot remove message3 again
    rm_data = {
        'token': user1['token'],
        'message_id': message3['message_id'],
    }
    response = requests.delete(url + 'message/remove', json=rm_data)
    assert response.status_code == 400

def test_sendlater(url):
    '''Tests the calling of message_sendlater function'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()
    assert 'channel_id' in channel1

    # user1 sends a message to channel1 10 seconds later
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 200
    message1 = response.json()
    assert 'message_id' in message1

def test_sendlater_invalid_inputs(url):
    '''Tests the calling of message_sendlater function with invalid inputs'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }

    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()
    assert 'channel_id' in channel1

    # user1 sends a message to channel1 10 seconds later
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 200
    message1 = response.json()
    assert 'message_id' in message1

    # test with invalid channel_id
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'] + 10,
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 400

    # test with invalid token
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': INVALID_TOKEN,
        'channel_id': channel1['channel_id'],
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 400

    # test with long message
    long_message = 'x' * 1010
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': long_message,
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 400

    # test with time in the past
    now = datetime.datetime.now()
    sec_later = now - datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 400

    # register and login user2
    reg_data2 = {
        'email': 'test2@email.com',
        'password': 'test2_pass',
        'name_first': 'test2_first',
        'name_last': 'test2_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data2)
    user2 = response.json()

    # user2 cannot send to channel1
    now = datetime.datetime.now()
    sec_later = now + datetime.timedelta(seconds=10)
    time_sent = sec_later.timestamp()

    msg_data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Hello World',
        'time_sent': time_sent,
    }
    response = requests.post(url + 'message/sendlater', json=msg_data)
    assert response.status_code == 400

def test_pin(url):
    '''Tests the calling of message_pin and message_unpin functions'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning',
    }
    response = requests.post(url + 'message/send', json=msg_data)
    message = response.json()
    assert 'message_id' in message

    # user1 pins the message
    pin_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 200
    assert response.json() == {}

    # check message details using channel/messages
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert 'messages' in msgs
    assert len(msgs['messages']) == 1
    message0 = msgs['messages'][0]
    assert 'is_pinned' in message0
    assert message0['is_pinned']

    # user1 unpins the message
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 200
    assert response.json() == {}

    # check message details again using channel/messages
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert 'messages' in msgs
    assert len(msgs['messages']) == 1
    message0 = msgs['messages'][0]
    assert 'is_pinned' in message0
    assert not message0['is_pinned']

def test_pin_invalid_inputs(url):
    '''Tests the calling of message_pin
     and message_unpin functions with invalid inputs'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning',
    }
    response = requests.post(url + 'message/send', json=msg_data)
    message = response.json()
    assert 'message_id' in message

    # test with invalid message id
    pin_data = {
        'token': user1['token'],
        'message_id': message['message_id'] + 10,
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 400

    # register and login user2
    reg_data2 = {
        'email': 'test2@email.com',
        'password': 'test2_pass',
        'name_first': 'test2_first',
        'name_last': 'test2_last',
    }

    response = requests.post(url + 'auth/register', json=reg_data2)
    user2 = response.json()

    # user2 cannot pin the message
    pin_data = {
        'token': user2['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 400

    # user2 join channel1
    join_data = {
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
    }
    response = requests.post(url + 'channel/join', json=join_data)
    assert response.status_code == 200

    # user2 still cannot pin the message because user2 is not an owner
    pin_data = {
        'token': user2['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 400

    # test pin with invalid token
    pin_data = {
        'token': INVALID_TOKEN,
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 400

    # user1 pins the message
    pin_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 200
    assert response.json() == {}

    # user1 cannot pin the message again
    response = requests.post(url + 'message/pin', json=pin_data)
    assert response.status_code == 400

    # test unpin with invalid message id
    pin_data = {
        'token': user1['token'],
        'message_id': message['message_id'] + 10,
    }
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 400

    # user2 cannot unpin the message
    pin_data = {
        'token': user2['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 400

    # test unpin with invalid token
    pin_data = {
        'token': INVALID_TOKEN,
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 400

    # user1 unpins the message
    pin_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
    }
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 200
    assert response.json() == {}

    # user1 cannot unpin the message again
    response = requests.post(url + 'message/unpin', json=pin_data)
    assert response.status_code == 400

def test_react(url):
    '''Tests the calling of message_react and message_unreact functions'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning',
    }
    response = requests.post(url + 'message/send', json=msg_data)
    message = response.json()
    assert 'message_id' in message

    # user1 reacts to the message
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    }
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 200
    assert response.json() == {}

    # check message details using channel/messages
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert 'messages' in msgs
    assert len(msgs['messages']) == 1
    message0 = msgs['messages'][0]
    assert 'reacts' in message0
    react0 = message0['reacts'][0]
    assert 'is_this_user_reacted' in react0
    assert react0['is_this_user_reacted']

    # user1 unreacts the message
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 200
    assert response.json() == {}

    # check message details again using channel/messages
    msgs_input = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'start': 0
    }
    response = requests.get(url + 'channel/messages', params=msgs_input)
    assert response.status_code == 200
    msgs = response.json()
    assert 'messages' in msgs
    assert len(msgs['messages']) == 1
    message0 = msgs['messages'][0]
    assert 'reacts' in message0
    assert not message0['reacts']

def test_react_invalid_inputs(url):
    '''Tests the calling of message_react
     and message_unreact functions with invalid inputs'''
    # register and login user1
    reg_data1 = {
        'email': 'test@email.com',
        'password': 'test_pass',
        'name_first': 'test_first',
        'name_last': 'test_last',
    }
    response = requests.post(url + 'auth/register', json=reg_data1)
    user1 = response.json()

    # user1 creates channel1
    channel_data1 = {
        'token': user1['token'],
        'name': 'channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json=channel_data1)
    channel1 = response.json()

    # user1 sends a message to channel1
    msg_data = {
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'message': 'Good morning',
    }
    response = requests.post(url + 'message/send', json=msg_data)
    message = response.json()
    assert 'message_id' in message

    # test react with invalid message id
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'] + 10,
        'react_id': 1,
    }
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 400

    # test react with invalid react id
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 10,
    }
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 400

    # test react with invalid token
    react_data = {
        'token': INVALID_TOKEN,
        'message_id': message['message_id'],
        'react_id': 1,
    }
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 400

    # user1 reacts to the message
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    }
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 200
    assert response.json() == {}

    # user1 cannot react to the message again
    response = requests.post(url + 'message/react', json=react_data)
    assert response.status_code == 400

    # test unreact with invalid message_id
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'] + 10,
        'react_id': 1,
    }
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 400

    # test unreact with invalid react_id
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 10,
    }
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 400

    # test unreact with invalid token
    react_data = {
        'token': INVALID_TOKEN,
        'message_id': message['message_id'],
        'react_id': 1,
    }
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 400

    # user1 unreacts the message
    react_data = {
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    }
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 200
    assert response.json() == {}

    # user1 cannot unreact the message again
    response = requests.post(url + 'message/unreact', json=react_data)
    assert response.status_code == 400
