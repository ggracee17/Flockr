'''
Message functions implementation
'''

from datetime import datetime
import threading
import jwt
import data
import error

def message_send(token, channel_id, message):
    '''
    Send a message from authorised_user to the channel specified by channel_id
    '''
    check_message_length(message)
    u_id = check_token_channel(token, channel_id)

    new_message_id = data.MAX_MESSAGE_ID + 1
    data.MAX_MESSAGE_ID = new_message_id

    time_created = datetime.now().timestamp()
    send_to_channel(channel_id, new_message_id, u_id, message, time_created)

    return {
        'message_id': new_message_id,
    }

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel
    specified by channel_id automatically at a specified time in the future
    '''
    check_message_length(message)
    check_channel_id(channel_id)
    u_id = check_token_channel(token, channel_id)

    new_message_id = data.MAX_MESSAGE_ID + 1
    data.MAX_MESSAGE_ID = new_message_id

    wait_period = time_sent - datetime.now().timestamp()
    if wait_period < 0:
        raise error.InputError(description='Time sent is a time in the past')

    timer = threading.Timer(
        wait_period, send_to_channel,
        args=(channel_id, new_message_id, u_id, message, time_sent)
    )
    timer.start()

    return {
        'message_id': new_message_id,
    }

def send_to_channel(channel_id, message_id, u_id, message, time_sent):
    '''
    Helper function that sends a given message to a given channel
    '''
    message_info = {
        'message_id' : message_id,
        'u_id' : u_id,
        'message' : message,
        'time_created' : time_sent,
        'reacts': [],
        'is_pinned': False,
    }

    for channel in data.channels:
        if channel_id == channel['channel_id']:
            channel['messages'].append(message_info)

def message_remove(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel
    '''
    u_id = check_token(token)

    removed = False
    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if (u_id == msg['u_id']) or check_owner(u_id, channel['channel_id']):
                    channel['messages'].remove(msg)
                    removed = True
                else:
                    raise error.AccessError(description='User does not have permission')

    if not removed:
        raise error.InputError(description='Message does not exist')

    return {
    }

def message_edit(token, message_id, message):
    '''
    Given a message, update it's text with new text.
    If the new message is an empty string, the message is deleted.
    '''
    u_id = check_token(token)
    check_message_length(message)

    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if (u_id == msg['u_id']) or check_owner(u_id, channel['channel_id']):
                    if not message:
                        channel['messages'].remove(msg)
                    else:
                        msg['message'] = message
                else:
                    raise error.AccessError(description='User does not have permission')
    return {
    }

def message_pin(token, message_id):
    '''
    Given a message within a channel, mark it as "pinned"
    '''
    u_id = check_token(token)

    pinned = False
    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if msg['is_pinned']:
                    raise error.InputError(description='Message is already pinned')
                if not check_member(u_id, channel['channel_id']):
                    raise error.AccessError(description='User is not a member of the channel')
                if not check_owner(u_id, channel['channel_id']):
                    raise error.AccessError(description='User is not an owner')

                msg['is_pinned'] = True
                pinned = True

    if not pinned:
        raise error.InputError(description='Message does not exist')

    return {}

def message_unpin(token, message_id):
    '''
    Given a message within a channel, remove it's mark as unpinned
    '''
    u_id = check_token(token)

    unpinned = False
    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if not msg['is_pinned']:
                    raise error.InputError(description='Message is already unpinned')
                if not check_member(u_id, channel['channel_id']):
                    raise error.AccessError(description='User is not a member of the channel')
                if not check_owner(u_id, channel['channel_id']):
                    raise error.AccessError(description='User is not an owner')

                msg['is_pinned'] = False
                unpinned = True

    if not unpinned:
        raise error.InputError(description='Message does not exist')

    return {}

def message_react(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of,
    add a "react" to that particular message
    '''
    u_id = check_token(token)
    check_react_id(react_id)

    reacted = False
    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if not check_member(u_id, channel['channel_id']):
                    raise error.InputError(description='User is not a member of the channel')

                add_react(msg['reacts'], react_id, u_id)
                reacted = True

    if not reacted:
        raise error.InputError(description='Message does not exist')

    return {}

def message_unreact(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of,
    remove a "react" to that particular message
    '''
    u_id = check_token(token)
    check_react_id(react_id)

    unreacted = False
    for channel in data.channels:
        for msg in channel['messages']:
            if msg['message_id'] == message_id:
                if not check_member(u_id, channel['channel_id']):
                    raise error.InputError(description='User is not a member of the channel')

                remove_react(msg['reacts'], react_id, u_id)
                unreacted = True

    if not unreacted:
        raise error.InputError(description='Message does not exist')

    return {}

def check_message_length(message):
    '''
    Check if the given massage has valid length
    '''
    if len(message) > 1000:
        raise error.InputError(description='Message is more than 1000 characters long')

def check_token(token):
    '''
    Check if given token is valid, if so return the associate u_id
    '''
    if token not in data.tokens:
        raise error.AccessError(description='Invalid token')

    decoded_info = jwt.decode(token, data.SECRET, algorithms=['HS256'])
    return decoded_info['u_id']

def check_channel_id(channel_id):
    '''
    Check if given channel_id is valid
    '''
    c_id_list = []
    for channel in data.channels:
        c_id_list.append(channel['channel_id'])
    if channel_id not in c_id_list:
        raise error.InputError(description='Invalid channel_id')

def check_token_channel(token, channel_id):
    '''
    Check if given token is a valid user that has joined the given channel
    '''
    if token not in data.tokens:
        raise error.AccessError(description='Invalid token')

    decoded_info = jwt.decode(token, data.SECRET, algorithms=['HS256'])
    u_id = decoded_info['u_id']

    member_list = []
    for channel in data.channels:
        if channel_id == channel['channel_id']:
            for member in channel['all_members']:
                member_list.append(member['u_id'])
    if u_id not in member_list:
        raise error.AccessError(description='User is not authorised')

    return u_id

def check_member(u_id, channel_id):
    '''
    Check if the given user is a member of the given channel
    '''
    for channel in data.channels:
        if channel_id == channel['channel_id']:
            for member in channel['all_members']:
                if u_id == member['u_id']:
                    return True
    return False

def check_owner(u_id, channel_id):
    '''
    Check if the given user is an owner of flocker or the given channel
    '''
    for user in data.users:
        if u_id == user['u_id']:
            if user['permission_id'] == 1:
                return True

    for channel in data.channels:
        if channel_id == channel['channel_id']:
            for member in channel['owner_members']:
                if u_id == member['u_id']:
                    return True
    return False

def check_react_id(react_id): 
    ''' 
    Check if given react_id is valid 
    ''' 
    if react_id != 1: 
        raise error.InputError(description='Invalid react_id') 

def add_react(reacts, react_id, u_id):
    '''
    Adds a react of given id by the given user
    '''
    if not reacts:
        reacts.append(
            {
                'react_id': react_id,
                'u_ids': [u_id],
            }
        )
    else:
        for react in reacts:
            # There is only one react_id and was checked earlier,
            # therefore it is assumed that there is only one element in the list
            if u_id in react['u_ids']:
                raise error.InputError(description='Message is already reacted by the user')

            react['u_ids'].append(u_id)

def remove_react(reacts, react_id, u_id):
    '''
    Removes a react of given id by the given user
    '''
    if not reacts:
        raise error.InputError(description='No active react')
    
    for react in reacts:
        # There is only one react_id and was checked earlier,
        # therefore it is assumed that there is only one element in the list
        if u_id not in react['u_ids']:
            raise error.InputError(description='Message has not been reacted by the user')
        react['u_ids'].remove(u_id)
        if not react['u_ids']:
            reacts.remove(react)
