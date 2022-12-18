"""Tests the auth.py functions"""

import pytest
import auth
import other
import user
# import data
from error import InputError

def test_auth_login():
    """Tests intended use of auth_login"""
    other.clear()

    # Registers 3 users and then checks if they can be logged inm

    test_id = auth.auth_register('test@email.com', 'test_password',
                                 'test_first', 'test_last')['u_id']

    another_id = auth.auth_register('another@email.com', 'another_password',
                                    'another_first', 'another_last')['u_id']

    final_id = auth.auth_register('final@email.com', 'final_password',
                                  'final_first', 'final_last')['u_id']

    assert auth.auth_login('test@email.com', 'test_password')['u_id'] == test_id
    assert auth.auth_login('another@email.com', 'another_password')['u_id'] == another_id
    assert auth.auth_login('final@email.com', 'final_password')['u_id'] == final_id

def test_auth_login_not_registered():
    """Tests logging in in auth_login while not registered """
    other.clear()
    with pytest.raises(InputError):
        assert auth.auth_login('test@email.com', 'test_password')

def test_auth_login_invalid_email():
    """Tests logging in with an invalid email in auth_login"""
    other.clear()

    # Checks for if the user tries the wrong email, their user id, and their first name

    test_id = auth.auth_register('test@email.com', 'test_password',
                                 'test_first', 'test_last')['u_id']

    with pytest.raises(InputError):
        assert auth.auth_login('wrong@email.com', 'test_password')
    with pytest.raises(InputError):
        assert auth.auth_login(test_id, 'test_password')
    with pytest.raises(InputError):
        assert auth.auth_login('test_first', 'test_password')

def test_auth_login_invalid_password():
    """Tests logging in with the wrong password in auth_login"""
    other.clear()

    auth.auth_register('test@email.com', 'test_password',
                       'test_first', 'test_last')

    with pytest.raises(InputError):
        assert auth.auth_login('test@email.com', 'wrong_password')

def test_auth_logout():
    """Tests intended use of auth_logout"""
    other.clear()

    # Tests logging out after registering while someone else is and isn't logged in,
    # logging out after logging in, Logging out while not logged in,
    # logging out using an invalid token

    test_token = auth.auth_register('test@email.com', 'test_password',
                                    'test_first', 'test_last')['token']

    another_token = auth.auth_register('another@email.com', 'another_password',
                                       'another_first', 'another_last')['token']

    assert auth.auth_logout(another_token)['is_success']
    assert auth.auth_logout(test_token)['is_success']
    test_token = auth.auth_login('test@email.com', 'test_password')['token']
    assert auth.auth_logout(test_token)['is_success']
    assert not auth.auth_logout(test_token)['is_success']
    assert not auth.auth_logout('An invalid token')['is_success']

def test_auth_register():
    """Tests intended use of auth_register"""
    other.clear()

    # Tests registering two users, ensuring they get registered with correct details

    test_dict = auth.auth_register('test@email.com', 'test_password',
                                   'test_first', 'test_last')

    test_dict_return = user.user_profile(test_dict['token'], test_dict['u_id'])
    assert test_dict_return['user']['u_id'] == test_dict['u_id']
    assert test_dict_return['user']['email'] == 'test@email.com'
    assert test_dict_return['user']['name_first'] == 'test_first'
    assert test_dict_return['user']['name_last'] == 'test_last'
    assert len(test_dict_return['user']['handle_str']) <= 20

    another_dict = auth.auth_register('another@email.com', 'test_password',
                                      'test_first', 'test_last')

    another_dict_return = user.user_profile(another_dict['token'], another_dict['u_id'])
    assert another_dict_return['user']['u_id'] == another_dict['u_id']
    assert another_dict_return['user']['email'] == 'another@email.com'
    assert another_dict_return['user']['name_first'] == 'test_first'
    assert test_dict_return['user']['name_last'] == 'test_last'
    assert len(test_dict_return['user']['handle_str']) <= 20

def test_auth_register_handle_reassignment():
    """Tests handle reassignment for auth_register
    when there is already a user with your default handle"""
    other.clear()

    # Registers 10 users and checks to make sure that the 10th user registered has
    # a handle with an appropriate length

    auth.auth_register('test@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test1@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test2@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test3@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test4@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test5@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test6@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test7@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test8@email.com', 'test_password', 'test_first', 'test_last')
    auth.auth_register('test9@email.com', 'test_password', 'test_first', 'test_last')
    test_dict = auth.auth_register('test10@email.com', 'test_password', 'test_first', 'test_last')
    test_dict_return = user.user_profile(test_dict['token'], test_dict['u_id'])
    assert len(test_dict_return['user']['handle_str']) <= 20

def test_auth_register_first_name_bounds():
    """Tests the bounds for first name size for auth_register"""
    other.clear()

    # Checks users with first names too long or short can't be registered

    short_f_id = auth.auth_register('short_f@email.com', 'test_password',
                                    'L', 'test_last')['u_id']

    assert auth.auth_login('short_f@email.com', 'test_password')['u_id'] == short_f_id

    long_f_id = auth.auth_register('long_f@email.com', 'test_password',
                                   '50_character_first_name____50_character_first_name',
                                   'test_last')['u_id']

    assert auth.auth_login('long_f@email.com', 'test_password')['u_id'] == long_f_id
    with pytest.raises(InputError):
        assert auth.auth_register('test@email.com', 'test_password',
                                  '51_character_first_name_____51_character_first_name',
                                  'test_last')
    with pytest.raises(InputError):
        assert auth.auth_register('test@email.com', 'test_password', '', 'test_last')

def test_auth_register_last_name_bounds():
    """Tests the bounds for last name size for auth_register"""
    other.clear()

    # Checks users with last names too long or short can't be registered

    short_l_id = auth.auth_register('short_l@email.com', 'test_password', 'test_first', 'L')['u_id']
    assert auth.auth_login('short_l@email.com', 'test_password')['u_id'] == short_l_id

    long_l_id = auth.auth_register('long_l@email.com', 'test_password', 'test_first',
                                   '50_character_last_name______50_character_last_name')['u_id']

    assert auth.auth_login('long_l@email.com', 'test_password')['u_id'] == long_l_id
    with pytest.raises(InputError):
        assert auth.auth_register('test@email.com', 'test_password', 'test_first', '')
    with pytest.raises(InputError):
        assert auth.auth_register('test@email.com', 'test_password', 'test_first',
                                  '51_character_last_name_______51_character_last_name')

def test_auth_register_passwrd_bounds():
    """Tests the bounds for password size for auth_register"""
    other.clear()

    # Checks users with passwords too short can't be registered

    short_p_id = auth.auth_register('short_p@email.com', '6_char',
                                    'test_first', 'test_last')['u_id']

    assert auth.auth_login('short_p@email.com', '6_char')['u_id'] == short_p_id
    with pytest.raises(InputError):
        assert auth.auth_register('another@email.com', '6char', 'test_first', 'test_last')

def test_auth_register_already_registered():
    """Tests for registering in auth_register using a taken email"""
    other.clear()
    auth.auth_register('test@email.com', 'test_password', 'test_first', 'test_last')
    with pytest.raises(InputError):
        assert auth.auth_register('test@email.com', 'test_password', 'test_first', 'test_last')

def test_auth_register_invalid_email():
    """Tests for registering in auth_register using an invalid email"""
    other.clear()
    with pytest.raises(InputError):
        assert auth.auth_register('email', 'test_password', 'test_first', 'test_last')

def test_auth_passwordreset_request():
    """Tests the intended use of auth_passwordreset_request"""
    other.clear()
    assert auth.auth_passwordreset_request('flockrtestuser@gmail.com') == {}
    auth.auth_register('flockrtestuser@gmail.com', 'test_password', 'test_first', 'test_last')
    assert auth.auth_passwordreset_request('test@email.com') == {}
    auth.auth_register('test@email.com', 'test_password', 'test_first', 'test_last')
    assert auth.auth_passwordreset_request('flockrtestuser@gmail.com') == {}
    assert auth.auth_passwordreset_request('flockrtestuser@gmail.com') == {}
    assert auth.auth_passwordreset_request('test@email.com') == {}
    assert auth.auth_passwordreset_request('flockrtestuser@gmail.com') == {}

def test_auth_passwordreset_reset():
    """Tests the error handling of auth_passwordreset_reset"""
    other.clear()

    # Tests than an input error is raised when an invalid reset code is used
    with pytest.raises(InputError):
        assert auth.auth_passwordreset_reset('invalid_code', 'new_password')

    # Would test that an input error is raised when an invalid password
    # (less than 6 characters) is entered, but because there is no way to get
    # a valid code, the assert will always pass as long as invalid code checking
    # works properly and raises its own input error
    with pytest.raises(InputError):
        assert auth.auth_passwordreset_reset('invalid_code', 'short')

# def test_password_reset_white_box():
#    """Some illegal white box testing for auth_passwordreset functions"""
#    other.clear()
#    test_id = auth.auth_register('flockrtestuser@gmail.com', 'test_password',
#                                 'test_first', 'test_last')['u_id']
#    assert auth.auth_passwordreset_request('flockrtestuser@gmail.com') == {}
#    for key in data.reset_codes:
#        if data.reset_codes[key] == 'flockrtestuser@gmail.com':
#            reset_code = key
#            assert auth.auth_passwordreset_reset(reset_code, 'new_password') == {}
#            assert auth.auth_login('flockrtestuser@gmail.com', 'new_password')['u_id'] == test_id
