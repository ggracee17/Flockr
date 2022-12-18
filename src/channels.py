'''
Channels functions implementation
'''

import jwt
import data
import error

def channels_list(token):
    '''
    Provide a list of all channels (and their associated details)
    that the authorised user is part of
    '''
    u_id = check_token(token)

    return_list = []
    for channel in data.channels:
        member_list = []
        for member in channel['all_members']:
            member_list.append(member['u_id'])

        if u_id in member_list:
            return_list.append(
                {
                    'channel_id': channel['channel_id'],
                    'name': channel['name']
                }
            )

    return {
        'channels': return_list,
    }

def channels_listall(token):
    '''
    Provide a list of all channels (and their associated details)
    '''
    check_token(token)
    return_list = []

    for channel in data.channels:
        return_list.append(
            {
                'channel_id': channel['channel_id'],
                'name': channel['name']
            }
        )

    return {
        'channels': return_list,
    }

def channels_create(token, name, is_public):
    '''
    Creates a new channel with that name that is either a public or private channel
    '''
    u_id = check_token(token)
    if len(name) > 20:
        raise error.InputError(description='Name is more than 20 characters long')

    for user in data.users:
        if u_id == user['u_id']:
            creator = user

    new_channel = {
        'channel_id' : len(data.channels) + 1,
        'name' : name,
        'is_public': is_public,
        'owner_members' : [
            creator
        ],
        'all_members' : [
            creator
        ],
        'messages': []
    }

    data.channels.append(new_channel)

    return {
        'channel_id': len(data.channels),
    }

def check_token(token):
    '''
    Checks if a given token is valid, returns the associated u_id if valid
    '''

    if token not in data.tokens:
        raise error.AccessError(description='Invalid token')
    decoded_info = jwt.decode(token, data.SECRET, algorithms=['HS256'])
    return decoded_info['u_id']
