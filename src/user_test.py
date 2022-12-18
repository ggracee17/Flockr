"""
Testing user functions
"""
import pytest
import auth
import user
import other
from error import InputError, AccessError

def test_user_profile():
    '''
    Test user profile
    '''
    other.clear()
    test_dict = auth.auth_register('test@email.com', 'test_password', 'test_first', 'test_last')
    test_dict_return = user.user_profile(test_dict['token'], test_dict['u_id'])
    assert test_dict_return['user']['u_id'] == test_dict['u_id']
    assert test_dict_return['user']['email'] == 'test@email.com'
    assert test_dict_return['user']['name_first'] == 'test_first'
    assert test_dict_return['user']['name_last'] == 'test_last'
    assert len(test_dict_return['user']['handle_str']) <= 20

def test_user_profile_two():
    '''
    Test user profile
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', \
                        'test_first', 'test_last')
    user2 = auth.auth_register('user2@email.com', 'test_password2', \
                        'test_first2', 'test_last2')
    assert user.user_profile(user1['token'], user1['u_id'])
    assert user.user_profile(user2['token'], user2['u_id'])

def test_user_profile_logged_out():
    '''
    Test user profile with logged out user
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', \
                        'test_first', 'test_last')
    user2 = auth.auth_register('user2@email.com', 'test_password2', \
                        'test_first2', 'test_last2')
    user.user_profile(user1['token'], user1['u_id'])
    user.user_profile(user2['token'], user2['u_id'])
    auth.auth_logout(user2['token'])
    with pytest.raises(AccessError):
        assert user.user_profile(user2['token'], user2['u_id'])

def test_user_profile_invalid_user():
    '''
    Test user profile with invalid user token
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', \
                        'test_first', 'test_last')

    with pytest.raises(InputError):
        assert user.user_profile(user1['token'], 'invalid user')

def test_user_profile_invalid_token():
    '''
    Test invalid user token
    '''
    other.clear()
    user1 = auth.auth_register('test@email.com', 'test_password', \
                        'test_first', 'test_last')
    with pytest.raises(AccessError):
        assert user.user_profile('invalid token', user1['u_id'])

def test_user_profile_no_user():
    '''
    Test user profile with no users
    '''
    other.clear()

    with pytest.raises(AccessError):
        assert user.user_profile('invalid token', 'invalid user')

def test_user_profile_setname():
    '''
    Test user_profile set name
    '''
    other.clear()

    auth.auth_register("another@email.com", "another_pass", "first", "last")
    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    u_id1 = user1['u_id']

    user.user_profile_setname(token1, "Bob", "Builder")
    user1_data = user.user_profile(token1, u_id1)

    assert user1_data['user']['name_first'] == "Bob"
    assert user1_data['user']['name_last'] == "Builder"

def test_user_profile_setname_invalid_token():
    '''
    Test user_profile set name
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    assert user.user_profile(user1['token'], user1['u_id'])

    with pytest.raises(AccessError):
        assert user.user_profile_setname('invalid_token', "Bob", "Builder")

def test_user_profile_setname_inputerror_firstname_long():

    '''
    Test user_profile set name with input error
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(InputError):
        assert user.user_profile_setname(token1, \
        "Beepboopboopbeepbeepboopbeepboopbeepboopbeepboopboop", "Builder")

def test_user_profile_setname_inputerror_lastname_long():

    '''
    Test user_profile set name with input error
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(InputError):

        assert user.user_profile_setname(token1, \
        "Bob", "BuilderBuilderBuilderBuilderBuilderBuilderBuilderBuilder")

def test_user_profile_setname_inputerror_firstname_short():

    '''
    Test user_profile set name with input error
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(InputError):
        assert user.user_profile_setname(token1, "", "Berry")
def test_user_profile_setname_inputerror_lastname_short():

    '''
    Test user_profile set name with input error
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(InputError):
        assert user.user_profile_setname(token1, "Cherry", "")

def test_user_profile_setname_inputerror_names_empty():

    '''
    Test user_profile set name with input error
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    with pytest.raises(InputError):
        assert user.user_profile_setname(token1, "", "")

def test_user_profile_setemail():

    '''
    Test user_profile set email
    '''
    other.clear()

    auth.auth_register("another@email.com", "another_pass", "first", "last")
    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    u_id1 = user1['u_id']
    user.user_profile_setemail(token1, "bob.builder@yahoo.com")
    user1_data = user.user_profile(token1, u_id1)

    email1 = user1_data['user']['email']

    assert email1 == "bob.builder@yahoo.com"

def test_user_profile_setemail_invalid_token():
    '''
    Test user_profile set name
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    assert user.user_profile(user1['token'], user1['u_id'])

    with pytest.raises(AccessError):
        assert user.user_profile_setemail('invalid_token', "bob.builder@yahoo.com")

def test_user_profile_setemail_inputerror_invalid_email():
    '''
    Test user_profile set email with input error invalid email
    '''

    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(InputError):
        assert user.user_profile_setemail(token1, "user2@.com")
    with pytest.raises(InputError):
        assert user.user_profile_setemail(token2, "@gmail.com")
    with pytest.raises(InputError):
        assert user.user_profile_setemail(token1, "user2@@hotmail.com")
    with pytest.raises(InputError):
        assert user.user_profile_setemail(token1, "user2@email.com")

def test_user_profile_setemail_inputerror_already_in_use():
    '''
    Test user_profile set email with input error existing user
    '''

    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(InputError):
        assert user.user_profile_setemail(token1, "user2@email.com")
    with pytest.raises(InputError):
        assert user.user_profile_setemail(token1, "test@email.com")
    with pytest.raises(InputError):
        assert user.user_profile_setemail(token2, "test@email.com")

def test_user_profile_sethandle():
    '''
    Test user_profile set email
    '''
    other.clear()

    auth.auth_register("another@email.com", "another_pass", "first", "last")
    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    u_id1 = user1['u_id']
    user.user_profile_sethandle(token1, "creativename")
    user1_data = user.user_profile(token1, u_id1)

    handle1 = user1_data['user']['handle_str']

    assert handle1 == "creativename"

def test_user_profile_sethandle_invalid_token():
    '''
    Test user_profile set email with invalid token
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    assert user.user_profile(user1['token'], user1['u_id'])

    with pytest.raises(AccessError):
        assert user.user_profile_sethandle('invalid token', "creativename")

def test_user_profile_sethandle_inputerror_invalid_token():
    '''
    Test user_profile set handle with input error invalid length and repeat
    '''
    other.clear()

    user1 = auth.auth_register("test@email.com", "test_pass", "First", "Last")
    token1 = user1['token']
    u_id1 = user1['u_id']
    user1_data = user.user_profile(token1, u_id1)
    handle1 = user1_data['user']['handle_str']

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(InputError):
        assert user.user_profile_sethandle(token2, handle1)

def test_user_profile_sethandle_inputerror_invalid_handle():
    '''
    Test user_profile set handle with input error invalid length and repeat
    '''
    other.clear()

    user2 = auth.auth_register("user2@email.com", "password2", "First2", "Last2")
    token2 = user2['token']

    with pytest.raises(InputError):
        assert user.user_profile_sethandle(token2, 'a')
