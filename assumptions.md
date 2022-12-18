Auth functions:


- As registering returns a token, and tokens are deleted when a user logs out, it is assumed that registering a user also logs them in.


- It was assumed that no more than 100 users would have a first name and last name that would result in the same handle. For example, the 101st user to attempt to get the handle qwertyuiopqwertyuiop would get qwertyuiopqwertyui100 instead of qwertyuiopqwertyu100, resulting in a 21 character handle, which is not allowed.


- As it is impossible to register a user with an invalid email, the auth_login function does not account for invalid emails, nor does its associated testing. The only time this would be a problem would be if a user with an invalid email was manually added to the user list, which would cause the user to be able to log in without getting an input error for inputting an invalid email. It was assumed that this manual entering would not occur and therefore doesn't require accounting for.


- It was assumed that "between 1 and 50 characters" meant that names could be no shorter than 1 character long and no longer than 50, not no shorter than 2 and no longer than 49.


- It is assumed that despite the fact an Access error is supposed to be raised in all functions (except auth_login and auth_register) when an invalid token is inputted, auth_logout should not raise an access error, as tokens are invalidated to log users out, meaning the only way for the function to fail logging a user out and return "'is_success': False" would be for an invalid token to be inputted.


- It is assumed that when a reset code is generated, the previous reset code is deleted to prevent old codes from not being removed.


- It is assumed that when a reset code is used, it is deleted so that it cannot be used again.


Channel functions:


- It was assumed that any member of a channel can invite users regardless of whether the channel is private or not. An input error will be raised if an invited user is already in the channel.


- When a channel is created, the creator automatically becomes a member and an owner of that channel.


- If the last owner leaves the channel, the entire channel will be deleted.

- Global owners becomes owners in all the channel they join

Channels functions:


- For testing channels functions, the max channel will be 40 as invalid channel_id has 45 added to it.

- If an user is not part of any channels when calling channels_list, a dictionary containing the 'channels' key will be returned with value being an empty list.


User functions:

- User_profile tests will assume a maximum of 40 user using the server as invalid u_id has 45 added to it 

- User_profile set name will raise error with first name first of both first name and last name length are invalid.

- User_profile set handle is 3-20 characters inclusively

- User_profile set handle and set email will raise error if it matches old values.

- User_profile upload photo will raise error in order of token, url, jpeg, crop dimensions.

- User_profile will raise error for image dimensions 0 by 0. It will also raise error for x_end and y_end being equal to x_start and y_start respectively

Standup functions:

- Token authentication issues in standup will raise AccessError in cases where the token is invalid or is valid but is not a member of channel.

- The errors raised from standup functions will be in order of token authentication, channel_id authentication, whether user is a member of channel, then message length for standup_send function.

- If a '/standup' message is send during active standup session it will raise error informing the user that one is already running

Other functions:


- To prevent the removal of all global owners, which would mean no one could be promoted to global owner, the first account to be registered is permanently a global owner and cannot be demoted. Attempting to demote them raises an access error.


- To prevent channel owners losing their channel ownership when losing their global ownership, global owners are not demoted to channel members when demoted globally.


- It is assumed that the permission that a user currently has is a valid permission, i.e. if a user's permission_id is changed to the same permission_id, an error is not raised.
