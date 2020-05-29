from .user import UserApi, FilteredUsersApi, ProfileImageApi, UnauthorizedUserApi, OnlineUserApi
from .auth import SignupApi, SigninApi, VerifyApi
from .chat import ChatsApi, ChatApi, GroupsApi, GroupApi, GroupImageApi
from .contact import ContactsApi, FilteredContactsApi, InvitationsApi


def initialize_routes(api):
    api.add_resource(UserApi, '/api/user')
    api.add_resource(UnauthorizedUserApi, '/api/user/<login>')
    api.add_resource(FilteredUsersApi, '/api/users/<login>')
    api.add_resource(ProfileImageApi, '/api/user/image')
    api.add_resource(OnlineUserApi, '/api/user/check_status/<login>')
    api.add_resource(ContactsApi, '/api/contacts')
    api.add_resource(FilteredContactsApi, '/api/contacts/<login>')
    api.add_resource(InvitationsApi, '/api/invitations')
    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(SigninApi, '/api/auth/signin')
    api.add_resource(VerifyApi, '/api/auth/is_token_valid')
    api.add_resource(ChatsApi, '/api/chats')
    api.add_resource(ChatApi, '/api/chat/<chat_id>')
    api.add_resource(GroupImageApi, '/api/group/image/<chat_id>')
    api.add_resource(GroupsApi, '/api/groups')
    api.add_resource(GroupApi, '/api/group/<group_id>')
