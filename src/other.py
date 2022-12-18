'''
Other functions implementation
'''

import jwt
import data
from error import InputError, AccessError

def clear():
    '''
    Resets the internal data of the application to it's initial state
    '''
    data.users.clear()
    data.channels.clear()
    data.tokens.clear()
    data.MAX_MESSAGE_ID = 0
    data.reset_codes.clear()
    return {}


def users_all(token):
    '''
    Returns a list of all users and their associated details
    '''
    if token not in data.tokens:
        raise AccessError(description='Invalid token')

    users_list = []
    for user in data.users:
        info = {
            'u_id': user['u_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str'],
        }
        if 'profile_img_url' in user: # pragma: no cover
            info['profile_img_url'] = user['profile_img_url']
        users_list.append(info)

    return {
        'users': users_list
    }

def admin_userpermission_change(token, u_id, permission_id):
    '''Takes a user based on u_id and changes their permission_id
    if the user associated with the given token has global permissions'''

    if u_id == 1:
        raise AccessError(description='Cannot change permissions of initial user')

    if u_id > len(data.users) or u_id < 1:
        raise InputError(description='Invalid user ID')

    valid_permission_id = [1, 2]

    if permission_id not in valid_permission_id:
        raise InputError(description='Invalid permission ID')


    if token not in data.tokens:
        raise AccessError(description='Invalid token')

    owner_id = jwt.decode(token, data.SECRET, algorithms=['HS256'])['u_id']

    # Checks owner_id - 1 since lists are indexed at 0 but the ids start at 1
    if data.users[owner_id - 1]['permission_id'] == 2:
        raise AccessError(description='Invalid user permissions')

    data.users[u_id - 1]['permission_id'] = permission_id

    # Returns if the user is not given owner permissions
    if permission_id == 2:
        return{}

    # Promotes the user to owner for all channels they are in that
    # they aren't currenlty an owner of
    for channel in data.channels:
        for member in channel['all_members']:
            if member['u_id'] == u_id:
                if member not in channel['owner_members']:
                    channel['owner_members'].append(member)

    return {}

def search(token, query_str):
    '''Returns a collection of messages from all the channels that the user
    is part of that contain the query string'''

    message_list = []

    # Converts token to u_id if it is valid
    if token not in data.tokens:
        raise AccessError(description='Invalid token')

    u_id = jwt.decode(token, data.SECRET, algorithms=['HS256'])['u_id']

    # Loops through every member of every channel. If the user associated
    # with the given token is a member, loops through every message
    # in that channel. If the message contains the query_str, it is added
    # to the returned message list.

    for channel in data.channels:
        for member in channel['all_members']:
            if member['u_id'] == u_id:
                for msg in channel['messages']:
                    if query_str in msg['message']:
                        message_list.append(msg)

    # Sets up 'is_user_reacted' key in each message
    for msg in message_list:
        set_if_reacted(msg['reacts'], u_id)

    return {
        'messages': message_list
    }

def set_if_reacted(all_reacts, u_id):
    '''
    Checks if the given user has reacted to the given message
    '''
    for react in all_reacts:
        if u_id in react['u_ids']:
            react['is_this_user_reacted'] = True
        else:
            react['is_this_user_reacted'] = False
