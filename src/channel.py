
'''
Channel functions implementation
'''

import jwt
import error
import data

def channel_invite(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately
    '''
    check_user_id(u_id)
    check_channel_id(channel_id)
    check_token(token, channel_id)

    # Check if user is already in the channel
    member_list = []
    for channel in data.channels:
        if channel_id == channel['channel_id']:
            for member in channel['all_members']:
                member_list.append(member['u_id'])
    if u_id in member_list:
        raise error.InputError(description='User is already a member of the channel')

    # Add given user to the given channel
    for user in data.users:
        if u_id == user['u_id']:
            invited_user = user

    for channel in data.channels:
        if channel_id == channel['channel_id']:
            channel['all_members'].append(invited_user)
            if invited_user['permission_id'] == 1:
                channel['owner_members'].append(invited_user)

    return {
    }

def channel_details(token, channel_id):
    '''
    Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel
    '''
    owner_list = []
    member_list = []

    check_channel_id(channel_id)
    check_token(token, channel_id)

    # Get details from data
    for channel in data.channels:
        if channel_id == channel['channel_id']:
            name = channel['name']
            for owner in channel['owner_members']:
                o_detail = {}
                o_detail['u_id'] = owner['u_id']
                o_detail['name_first'] = owner['name_first']
                o_detail['name_last'] = owner['name_last']

                if 'profile_img_url' in owner: # pragma: no cover
                    o_detail['profile_img_url'] = owner['profile_img_url']

                owner_list.append(o_detail)

            for member in channel['all_members']:
                m_detail = {}
                m_detail['u_id'] = member['u_id']
                m_detail['name_first'] = member['name_first']
                m_detail['name_last'] = member['name_last']

                if 'profile_img_url' in member: # pragma: no cover
                    m_detail['profile_img_url'] = member['profile_img_url']

                member_list.append(m_detail)

    return {
        'name': name,
        'owner_members': owner_list,
        'all_members': member_list,
    }


def channel_messages(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50".
    '''
    check_channel_id(channel_id)
    u_id = check_token(token, channel_id)

    # Get messages from the given channel
    for channel in data.channels:
        if channel_id == channel['channel_id']:
            messages_list = channel['messages']

    # Check if start value is valid
    if start > len(messages_list):
        raise error.InputError(description='Start is greater than total number of messages')

    end = start + 50
    stop = start + 50
    if end > len(messages_list):
        end = -1
        stop = len(messages_list)

    # Return messages within the range in chronological order
    reversed_messages = messages_list[::-1]
    return_messages = []
    for i in range(start, stop):
        return_messages.append(reversed_messages[i])

    # Set up 'is_user_reacted' key in each message
    for msg in return_messages:
        set_if_reacted(msg['reacts'], u_id)

    return {
        'messages': return_messages,
        'start': start,
        'end': end,
    }

def channel_leave(token, channel_id):
    '''
    User leaves the channel
    '''

    detail = find_channel(channel_id)
    valid_user = find_user(token)
    channel_members = check_member(valid_user['u_id'], detail)

    if not channel_members:
        raise error.AccessError('User is not a member of this channel')

    channel_owners = check_owner(valid_user['u_id'], detail)
    if not channel_owners:
        channel_members = remove_member(valid_user['u_id'], channel_members)
        detail['all_members'] = channel_members

    else:
        owner_count = len(channel_owners)

        if owner_count == 1:
            delete_entire_channel(channel_id)

        else:
            channel_owners = remove_owner(valid_user['u_id'], channel_owners)
            detail['owner_members'] = channel_owners
            channel_members = remove_member(valid_user['u_id'], channel_members)
            detail['all_members'] = channel_members

        for channel in data.channels:
            if channel['channel_id'] == channel_id:
                channel = detail

    return {
    }

def channel_join(token, channel_id):
    '''
    Join a channel
    '''
    detail = find_channel(channel_id)

    if not detail['is_public']:
        raise error.AccessError('This channel is private')

    user = find_user(token)

    for keys in detail:
        if keys == 'all_members':
            detail['all_members'].append(user)
        elif keys == 'owner_members' and user['permission_id'] == 1:
            detail['owner_members'].append(user)

    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail

    return {
    }

def channel_addowner(token, channel_id, u_id):
    '''
    Add another owner to channel
    '''
    detail = find_channel(channel_id)

    valid_user = find_user(token)
    channel_owners = check_owner(valid_user['u_id'], detail)

    if not channel_owners:
        raise error.AccessError('User does not have owner access')

    #confirm  u_id is not already owner
    for owner in channel_owners:
        if owner['u_id'] == u_id:
            raise error.InputError('User is already an owner')

    user = find_user_u_id(u_id)
    user = user.copy()

    if not check_member(user['u_id'], detail):
        for keys in detail:
            if keys == 'all_members':
                detail['all_members'].append(user)

    for keys in detail:
        if keys == 'owner_members':
            detail['owner_members'].append(user)

    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail

    return {
    }

def channel_removeowner(token, channel_id, u_id):
    '''
    Remove another owner from channel
    '''
    detail = find_channel(channel_id)
    remove_user = find_user_u_id(u_id)

    if remove_user['permission_id'] == 1:
        raise error.AccessError('Cannot remove global owner')

    valid_user = find_user(token)
    channel_owners = check_owner(valid_user['u_id'], detail)
    if not channel_owners:
        raise error.AccessError('User does not have owner access')

    #Checks if removing user is a valid owner
    channel_owners = check_owner(remove_user['u_id'], detail)
    if not channel_owners:
        raise error.InputError('User is not an owner')

    channel_owners = remove_owner(remove_user['u_id'], channel_owners)
    detail['owner_members'] = channel_owners

    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            channel = detail

    return {
    }

#Return a dictionary of the channel
def find_channel(channel_id):
    '''
    Check if channel exist
    '''
    if not data.channels:
        raise error.InputError(description="No channel has been created")

    for channel in data.channels:
        if channel['channel_id'] == channel_id:
            return channel

    raise error.InputError(description="Channel ID is not valid")

def find_user(token):
    '''
    Check if user exist through their token
    '''
    if token not in data.tokens:
        raise error.AccessError(description='Invalid token')

    decoded_info = jwt.decode(token, data.SECRET, algorithms=['HS256'])
    u_id = decoded_info['u_id']

    for user in data.users:
        if user['u_id'] == u_id:
            associated_user = user
    return associated_user

def find_user_u_id(u_id):
    '''
    Check if user exist through their u_id
    '''
    for user in data.users:
        if user['u_id'] == u_id:
            return user

    raise error.InputError('Invalid user ID')

def check_member(u_id, channel_fulldetail):
    '''
    Check if user is a member of channel
    '''
    for key in channel_fulldetail['all_members']:
        if key['u_id'] == u_id:
            return channel_fulldetail['all_members']

    return False

def check_owner(u_id, channel_fulldetail):
    '''
    Check if user is an owner of channel
    '''
    for key in channel_fulldetail['owner_members']:
        if key['u_id'] == u_id:
            return channel_fulldetail['owner_members']

    return False

def remove_member(u_id, channel_members):
    '''
    Remove a member from a channel
    '''
    for member in channel_members:
        if member["u_id"] == u_id:
            channel_members.remove(member)
    return channel_members

def remove_owner(u_id, channel_owners):
    '''
    Remove an owner from a channel
    '''
    for owner in channel_owners:
        if owner["u_id"] == u_id:
            channel_owners.remove(owner)
    return channel_owners

def delete_entire_channel(channel_id):
    '''
    Delete a channel with given channel_id
    '''
    for chan in data.channels:
        if chan['channel_id'] == channel_id:
            data.channels.remove(chan)

def check_channel_id(channel_id):
    '''
    Check if channel_id is valid
    '''
    c_id_list = []
    for channel in data.channels:
        c_id_list.append(channel['channel_id'])
    if channel_id not in c_id_list:
        raise error.InputError(description='Wrong channel_id')

def check_user_id(u_id):
    '''
    Check if user_id is valid
    '''
    u_id_list = []
    for user in data.users:
        u_id_list.append(user['u_id'])
    if u_id not in u_id_list:
        raise error.InputError(description='Wrong user_id')

def check_token(token, channel_id):
    '''
    Check if token is a valid user, return the associated u_id
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
        raise error.AccessError(description=\
        'You must be a member of the channel to view its details')

    return u_id

def set_if_reacted(all_reacts, u_id):
    '''
    Checks if the given user has reacted to the given message
    '''
    for react in all_reacts:
        if u_id in react['u_ids']:
            react['is_this_user_reacted'] = True
        else:
            react['is_this_user_reacted'] = False
