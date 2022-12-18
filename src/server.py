'''Server side of implementation'''

from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
import auth
import channel
import channels
import message
import user
import other
import standup
from error import InputError

def default_handler(err):
    '''Handles errors'''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)

@APP.route('/auth/login', methods=['POST'])
def login():
    '''Calls the login function from auth.py'''
    data = request.get_json()
    return dumps(
        auth.auth_login(
            data['email'], data['password']
        )
    )

@APP.route('/auth/logout', methods=['POST'])
def logout():
    '''Calls the logout function from auth.py'''
    data = request.get_json()
    return dumps(
        auth.auth_logout(
            data['token']
        )
    )

@APP.route('/auth/register', methods=['POST'])
def register():
    '''Calls the register function from auth.py'''
    data = request.get_json()
    return dumps(
        auth.auth_register(
            data['email'], data['password'], data['name_first'], data['name_last']
        )
    )

@APP.route('/auth/passwordreset/request', methods=['POST'])
def passwordreset_request():
    '''Calls the password reset request function from auth.py'''
    data = request.get_json()
    return dumps(
        auth.auth_passwordreset_request(
            data['email']
        )
    )

@APP.route('/auth/passwordreset/reset', methods=['POST'])
def passwordreset_reset():
    '''Calls the password reset function from auth.py'''
    data = request.get_json()
    return dumps(
        auth.auth_passwordreset_reset(
            data['reset_code'], data['new_password']
        )
    )

@APP.route("/channel/invite", methods=['POST'])
def channel_invite_flask():
    '''Calls the invite function from channel.py'''
    data = request.get_json()
    return dumps(
        channel.channel_invite(
            data['token'], data['channel_id'], data['u_id']
        )
    )

@APP.route("/channel/details", methods=['GET'])
def channel_details_flask():
    '''Calls the details function from channel.py'''
    return dumps(
        channel.channel_details(
            request.args.get('token'), int(request.args.get('channel_id'))
        )
    )

@APP.route("/channel/messages", methods=['GET'])
def channel_messages_flask():
    '''Calls the messages function from channel.py'''
    return dumps(
        channel.channel_messages(
            request.args.get('token'),
            int(request.args.get('channel_id')),
            int(request.args.get('start'))
        )
    )

@APP.route("/channel/leave", methods=['POST'])
def leave():
    '''Calls the leave function from channel.py'''
    data = request.get_json()
    return dumps(
        channel.channel_leave(data['token'], data['channel_id'])
    )

@APP.route("/channel/join", methods=['POST'])
def join():
    '''Calls the join function from channel.py'''
    data = request.get_json()
    return dumps(
        channel.channel_join(data['token'], data['channel_id'])
    )

@APP.route("/channel/addowner", methods=['POST'])
def addowner():
    '''Calls the addowner function from channel.py'''
    data = request.get_json()
    return dumps(
        channel.channel_addowner(
            data['token'], data['channel_id'], data['u_id']
        )
    )

@APP.route("/channel/removeowner", methods=['POST'])
def removeowner():
    '''Calls the removeowner function from channel.py'''
    data = request.get_json()
    return dumps(
        channel.channel_removeowner(
            data['token'], data['channel_id'], data['u_id']
        )
    )

@APP.route("/channels/list", methods=['GET'])
def channels_list_flask():
    '''Calls the list function from channels.py'''
    return dumps(
        channels.channels_list(request.args.get('token'))
    )

@APP.route("/channels/listall", methods=['GET'])
def channels_listall_flask():
    '''Calls the listall function from channels.py'''
    return dumps(
        channels.channels_listall(request.args.get('token'))
    )

@APP.route("/channels/create", methods=['POST'])
def channels_create_flask():
    '''Calls the create function from channels.py'''
    data = request.get_json()
    return dumps(
        channels.channels_create(
            data['token'], data['name'], data['is_public']
        )
    )

@APP.route("/message/send", methods=['POST'])
def message_send_flask():
    '''Calls the send function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_send(
            data['token'], data['channel_id'], data['message']
        )
    )

@APP.route("/message/remove", methods=['DELETE'])
def message_remove_flask():
    '''Calls the remove function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_remove(
            data['token'], data['message_id']
        )
    )

@APP.route("/message/edit", methods=['PUT'])
def message_edit_flask():
    '''Calls the edit function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_edit(
            data['token'], data['message_id'], data['message']
        )
    )

@APP.route("/message/sendlater", methods=['POST'])
def message_sendlater_flask():
    '''Calls the sendlater function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_sendlater(
            data['token'], data['channel_id'], data['message'], data['time_sent']
        )
    )

@APP.route("/message/pin", methods=['POST'])
def message_pin_flask():
    '''Calls the message_pin function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_pin(
            data['token'], data['message_id']
        )
    )

@APP.route("/message/unpin", methods=['POST'])
def message_unpin_flask():
    '''Calls the message_unpin function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_unpin(
            data['token'], data['message_id']
        )
    )

@APP.route("/message/react", methods=['POST'])
def message_react_flask():
    '''Calls the message_react function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_react(
            data['token'], data['message_id'], data['react_id']
        )
    )

@APP.route("/message/unreact", methods=['POST'])
def message_unreact_flask():
    '''Calls the message_unreact function from message.py'''
    data = request.get_json()
    return dumps(
        message.message_unreact(
            data['token'], data['message_id'], data['react_id']
        )
    )

@APP.route("/user/profile", methods=['GET'])
def profile():
    '''Calls the profile function from user.py'''
    return dumps(
        user.user_profile(
            request.args.get('token'), int(request.args.get('u_id'))
        )
    )

@APP.route("/user/profile/setname", methods=['PUT'])
def setname():
    '''Calls the setname function from user.py'''
    data = request.get_json()
    return dumps(
        user.user_profile_setname(
            data['token'], data['name_first'], data['name_last']
        )
    )

@APP.route("/user/profile/setemail", methods=['PUT'])
def setemail():
    '''Calls the setemail function from user.py'''
    data = request.get_json()
    return dumps(
        user.user_profile_setemail(data['token'], data['email'])
    )

@APP.route("/user/profile/sethandle", methods=['PUT'])
def sethandle():
    '''Calls the sethandle function from user.py'''
    data = request.get_json()
    return dumps(
        user.user_profile_sethandle(data['token'], data['handle_str'])
    )

@APP.route("/user/profile/uploadphoto", methods=['POST'])
def uploadphoto():
    '''Calls the uploadphoto function from user.py'''
    #Downloading and saving hte phtot
    data = request.get_json()
    path = user.user_profile_uploadphoto(data['token'], str(data['img_url']), \
        data['x_start'], data['y_start'], data['x_end'], data['y_end'])

    return dumps(path)

@APP.route("/static/<path:path>")
def send(path):
    #serving the photo
    '''Send profile picture'''
    return send_from_directory('', path)

@APP.route("/users/all", methods=['GET'])
def usersall():
    '''Calls the users_all function from other.py'''
    return dumps(
        other.users_all(request.args.get('token'))
    )

@APP.route("/standup/start", methods=['POST'])
def standup_start():
    '''Calls the standup_start function from user.py'''
    data = request.get_json()
    return dumps(
        standup.standup_start(data['token'], int(data['channel_id']), int(data['length']))
    )

@APP.route("/standup/active", methods=['GET'])
def standup_active():
    '''Calls the standup_active function from user.py'''
    return dumps(
        standup.standup_active(
            request.args.get('token'),
            int(request.args.get('channel_id')),
        )
    )

@APP.route("/standup/send", methods=['POST'])
def standup_send():
    '''Calls the standup_send function from user.py'''
    data = request.get_json()
    return dumps(
        standup.standup_send(data['token'], data['channel_id'], data['message'])
    )

@APP.route('/clear', methods=['DELETE'])
def clear():
    '''Calls the clear function from other.py'''
    return dumps(
        other.clear()
    )

@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_userpermission_change():
    '''Calls the admin user permission change function from other.py'''
    data = request.get_json()
    return dumps(
        other.admin_userpermission_change(
            data['token'], data['u_id'], data['permission_id']
        )
    )

@APP.route('/search', methods=['GET'])
def search():
    '''Calls the admin user permission change function from other.py'''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(
        other.search(
            token, query_str
        )
    )

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    '''Example'''
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
