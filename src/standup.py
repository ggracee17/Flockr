"""
Implementation of standup functions
"""
import threading
import time
from datetime import datetime
import error
import data
from channel import find_user, find_channel, check_member
from message import check_token_channel, send_to_channel

def standup_start(token, channel_id, length):
    '''
    Start standup session
    '''
    user = find_user(token)
    detail = find_channel(channel_id)
    if not check_member(user['u_id'], detail):
        raise error.AccessError(description="This user is not a member of this channel")

    if 'standup' in detail:
        raise error.InputError(description="Active standup already in session")

    finish = time.time() + length
    detail['standup'] = {'finish' : finish, 'messages': []}

    session = threading.Timer(length, function=standup_end, \
    args=(token, channel_id))
    session.start()
    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail
    return {'time_finish' : finish}

def standup_end(token, channel_id):
    '''
    End standup session
    '''
    find_user(token)
    detail = find_channel(channel_id)

    log = detail['standup']['messages']
    string = ''
    for entry in log:
        entry = entry.items()
        for item in entry:
            string = string + str(item[0]) + ' : ' + ''.join(item[1]) + '\n'
    del detail['standup']
    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail
    send_log(token, channel_id, string)

def standup_active(token, channel_id):
    '''
    Return the finish time for standup active session
    '''
    user = find_user(token)
    detail = find_channel(channel_id)
    if not check_member(user['u_id'], detail):
        raise error.AccessError(description="This user is not a member of this channel")

    active = False
    time_end = None
    if 'standup' in detail:
        active = True
        time_end = detail['standup']['finish']

    return {'is_active' : active, 'time_finish' : time_end}

def standup_send(token, channel_id, message):
    '''
    Send message to active standup session
    '''
    user = find_user(token)
    detail = find_channel(channel_id)
    if not check_member(user['u_id'], detail):
        raise error.AccessError(description="This user is not a member of this channel")

    if 'standup' not in detail:
        raise error.InputError(description="No active standup session")

    if '/standup' in message[:8]:
        raise error.InputError(description='Standup session already active')
    if len(message) > 1000:
        raise error.InputError(description="Message is too large")

    send = {user['handle_str']: {message}}
    detail['standup']['messages'].append(send)

    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail

    return {}

def send_log(token, channel_id, message):
    '''
    This returns a log of all the messages sent in standup.
    This code was copied from Grace's message_send function.
    '''
    u_id = check_token_channel(token, channel_id)

    new_message_id = data.MAX_MESSAGE_ID + 1
    data.MAX_MESSAGE_ID = new_message_id

    time_created = datetime.now().timestamp()
    send_to_channel(channel_id, new_message_id, u_id, message, time_created)
