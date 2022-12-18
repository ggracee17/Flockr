'''secret for jwt encoding'''
SECRET = 'ballast'

'''variable for generating message_ids in message_send and message_sendlater'''
MAX_MESSAGE_ID = 0

'''
user = {}

{
    'u_id' : 1,
    'email' : '123@gmail.com',
    'name_first' : 'Hayden',
    'name_last' : 'Jacobs',
    'handle_str' : ' ',
    'password': ' ',
    'permission_id': 2,
}
'''


users = []
'''
users = [
    {
        'u_id' : 1,
        'email' : 'test@gmail.com',
        'name_first' : 'Hayden',
        'name_last' : 'Jacobs',
        'handle_str' : ' ',
        'password': ' ',
        'permission_id': 1,
    },
    {
        'u_id' : 2,
        'email' : 'another@gmail.com',
        'name_first' : 'Sam',
        'name_last' : 'Smith',
        'handle_str' : ' ',
        'password': ' ',
        'permission_id': 2,
    }
]

'''

channels = []
'''
[
    {
        'channel_id' : 1,
        'name' : 'channel1',
        'is_public': True,
        'owner_members' : [
            {
                'u_id' : 1,
                'email' : 'test@gmail.com',
                'name_first' : 'Hayden',
                'name_last ' : 'Jacobs',
                'handle_str' : ' ',
                'password': ' ',
            }
        ],
        'all_members' : [
            {
                'u_id' : 1,
                'email' : 'test@gmail.com',
                'name_first' : 'Hayden',
                'name_last ' : 'Jacobs',
                'handle_str' : ' ',
                'password': ' ',
            },
            {
                'u_id' : 2,
                'email' : 'another@gmail.com',
                'name_first' : 'Sam',
                'name_last ' : 'Smith',
                'handle_str' : ' ',
                'password': ' ',
            }
        ],
        'messages' : [
            {
                'message_id' : 1,
                'u_id' : 1,
                'message' : 'Hello World',
                'time_created' : 12345677,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        #'is_this_user_reacted': False
                    },
                ],
                'is_pinned': False,
            },
            {
                'message_id' : 2,
                'u_id' : 2,
                'message' : 'Goodbye',
                'time_created' : 12345678,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        #'is_this_user_reacted': False
                    },
                ],
                'is_pinned': False,
            },
            {
                'message_id' : 3,
                'u_id' : 2,
                'message' : 'Iteration 1: Basic functionality and tests',
                'time_created' : 12345679,
                'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        #'is_this_user_reacted': False
                    },
                ],
                'is_pinned': False,
            },
        ]
    },
    {
        'channel_id' : 2,
        'name' : 'channel2',
        'is_public': True,
        'owner_members' : [
            {
                'u_id' : 2,
                'email' : 'another@gmail.com',
                'name_first' : 'Sam',
                'name_last ' : 'Smith',
                'handle_str' : ' ',
                'password': ' ',
            }
        ],
        'all_members' : [
            {
                'u_id' : 2,
                'email' : 'another@gmail.com',
                'name_first' : 'Sam',
                'name_last ' : 'Smith',
                'handle_str' : ' ',
                'password': ' ',
            }
        ],
        'messages' : [
            {
                'message_id' : 1,
                'u_id' : 1,
                'message' : 'Hello World',
                'time_created' : 1,
                [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        #'is_this_user_reacted': False
                    },
                ],
                'is_pinned': False,
            },
        ]
    }
]
'''

tokens = []
'''
[
    b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxfQ.
    hOT2PzNDMEW-UPlc5h6ZNUsDW-XOGASFmol9cJGdiUA',
    b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoyfQ.
    FKgeYBPr6Z56zpj06xtU7AB-eYicvXjUwJMvk3phjS4',
]
'''

reset_codes = {}
'''
{
    'eyJ0eXAiOi9KV1QiLC3h' : 'test@email.com',
    'eyJ0eXAiOi9KV1QiLC3h' : 'another@email.com',
}
'''
