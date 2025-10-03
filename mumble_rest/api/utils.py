"""
utils.py
Utilities used within the application.

:copyright: (C) 2014 by github.com/alfg.
:license:   MIT, see README for more details.
"""

from builtins import int
from dataclasses import dataclass
from django.utils import timezone
from ..mumble_ice import Meta, MumbleServer


def obj_to_dict(obj):
    """
    Used for converting objects from Murmur.ice into python dict.
    """
    rv = {'_type': str(type(obj))}

    if isinstance(obj, (bool, int, float, str)):
        return obj

    if type(obj) in (list, tuple):
        return [obj_to_dict(item) for item in obj]

    if type(obj) == dict:
        return dict((str(k), obj_to_dict(v)) for k, v in obj.items())

    return obj_to_dict(obj.__dict__)


def get_server_conf(meta, server, key):
    """
    Gets the server configuration for given server/key.
    """
    val = server.getConf(key)
    if '' == val:
        val = meta.getDefaultConf().get(key, '')
    return val


def get_server_port(meta, server, val=None):
    """
    Gets the server port value from configuration.
    """
    val = server.getConf('port') if val is None else val

    if '' == val:
        val = meta.getDefaultConf().get('port', 0)
        val = int(val) + server.id() - 1
    return int(val)


def get_all_users_count(meta):
    """
    Gets the entire list of users online count by iterating through servers.
    """
    user_count = 0
    for s in meta.getAllServers():
        user_count += (s.isRunning() and len(s.getUsers())) or 0
    return user_count


def get_active_username(server, user_name: str):
    """
    Gets the entire list of users online count by iterating through servers.
    """
    users = obj_to_dict(server.getUsers())
    for u in users.values():
        if user_name == u.get("name"):
            return u
    return False


def get_registered_user(server, uid):
    try:
        return server.getRegistration(uid)
    except MumbleServer.InvalidUserException:
        return False


def get_registered_users(server, search_str):
    return server.getRegisteredUsers(search_str)


def get_registered_user_ids(server):
    try:
        return [id for id, _ in server.getRegisteredUsers("").items()]
    except:
        return []


def get_registered_user_id(server, user_name: str):
    users = get_registered_users(server, user_name)
    for id, u in users.items():
        if u.lower() == user_name.lower():
            return id
    return False


def register_user(server, user_name: str):
    new_user = {

        MumbleServer.UserInfo.UserName: user_name,
        MumbleServer.UserInfo.UserComment: f"last updated {timezone.now()}"
    }
    uid = server.registerUser(new_user)
    return uid


def update_user_pass(server, user_name: str, password: str):
    uid = get_registered_user_id(server, user_name)
    user_pass = {
        MumbleServer.UserInfo.UserPassword: password,
        MumbleServer.UserInfo.UserHash: None,
        MumbleServer.UserInfo.UserComment: f"last updated {timezone.now()}"
    }
    server.updateRegistration(uid, user_pass)


def unregister_user(server, user_id: int):
    server.unregisterUser(user_id)


def check_user_pass(server, user_name: str, password: str):
    test = server.verifyPassword(user_name, password)
    results = {
        -1: f"Password Incorrect for {user_name}",
        -2: f"Unknown User ({user_name})"
    }
    return results.get(test, "Success")


def str_to_groups(groups_str):
    return groups_str.split(",")


def update_user_groups(server, user_name: str, password: str):
    uid = get_registered_user_id(server, user_name)
    user_pass = {
        MumbleServer.UserInfo.UserPassword: password,
        MumbleServer.UserInfo.UserHash: None,
        MumbleServer.UserInfo.UserComment: f"last updated {timezone.now()}"
    }
    server.updateRegistration(uid, password)


def get_channel_acls(server, chid: int):
    acls = []
    groups = []
    inherit = False
    acls, groups, inherit = server.getACL(chid)

    return acls, groups, inherit


@dataclass
class ACLGroup:
    name: str
    users: list[int]


def set_group_add(groups, group_name, add_ids):
    for group in groups:
        if group_name == group.name:
            group.add = add_ids
            return True
    return False


def filter_uids(server_uids, users):
    return [u for u in users if u in server_uids]


def set_channel_acls(server, chid: int, newGroup: list[ACLGroup] = []):
    acls = []
    groups = []
    inherit = False
    acls, groups, inherit = get_channel_acls(server, chid)
    server_uids = get_registered_user_ids(server)
    names = [g.name for g in groups]
    for g in newGroup:
        # Enforce UID's that are known otherwise boom!
        uids = filter_uids(server_uids, g.users)
        if g.name not in names:
            _g = MumbleServer.Group()
            _g.name = g.name
            _g.inherit = True
            _g.inheritable = True
            _g.add = uids
            groups.append(_g)
        elif g.name in names:
            set_group_add(groups, g.name, uids)
    server.setACL(chid, acls, groups, inherit)
    return acls, groups, inherit


STD_RESPONSES = {200: dict, 401: str, 402: str, 403: str, 404: str}
