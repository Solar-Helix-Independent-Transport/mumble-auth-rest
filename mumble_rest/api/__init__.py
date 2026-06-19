from datetime import timedelta
import logging
import random
import string
from typing import Any, Optional
from django.http import HttpRequest
from django.conf import settings
from mumble_rest.mumble_ice import Meta
from ninja import Form, NinjaAPI
from .servers import ServerEndpoints
from .users import UserEndpoints, get_registered_user
from .acls import ACLEndpoints
from .active import ActiveEndpoints
from .utils import ACLGroup, get_server_conf, get_server_port, check_user_pass, get_active_username, get_channel_acls, get_registered_user_id, obj_to_dict, register_user, set_channel_acls, unregister_user, update_user_pass
from .channels import ChannelImportRequest, export_channels, import_channels
from ninja.security import APIKeyHeader
from mumble_rest.models import APIKey
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)

class api_key(APIKeyHeader):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        test = False
        for t in APIKey.objects.all():
            _t = t.test(key)
            if _t:
                logger.info(f"{request} - {t.name} - success")
                test = True
                break
        return test


api = NinjaAPI(
    title="Mumble Rest",
    auth=[
        api_key()
    ],
    docs_decorator=staff_member_required
    # openapi_url=settings.DEBUG and "/openapi.json" or ""
)


@api.get(
    "/health-check",
    response={200: dict, 503: dict},
    tags=["Status"])
def get_status(request):
    """
        Mumble Health Check
    """
    try:
        s = Meta.meta.getVersion()
        ut = Meta.meta.getUptime()
        return 200, {'status': 'OK', "version": s, "uptime": ut}
    except Exception as e:
        return 503, {'status': 'NOTOK', "error": str(e)}


@api.get(
    "/user_count",
    response={200: dict, 503: dict},
    tags=["Status"])
def get_user_count(
    request,
    server_id: int = 0
):
    """
        Mumble Users
    """
    try:
        server = Meta.meta.getServer(server_id)
        return 200, (len(server.getUsers())) or 0
    except:
        return 503, {'status': 'NOTOK'}


@api.post(
    "/auth/user",
    response={
        200: dict,
        404: dict,
    },
    tags=["Auth"]
)
def post_auth_register_or_update(
    request,
    user_name: Form[str],
    user_pass: Form[str],
    server_id: int = 0
):
    server = Meta.meta.getServer(server_id)
    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    uid = get_registered_user_id(server, user_name)

    if uid:  # existing user update pass
        update_user_pass(server, user_name, user_pass)
    else:   # new user create and update
        uid = register_user(server, user_name)
        update_user_pass(server, user_name, user_pass)

    test = check_user_pass(server, user_name, user_pass)

    return 200, {
        "user_id": uid,
        "password_test": test,
    }


@api.post(
    "/auth/groups",
    response={
        200: dict,
        404: dict,
    },
    tags=["Auth"]
)
def post_auth_update_groups(
    request,
    groups: list[ACLGroup],
    server_id: int = 0,
    channel_id: int = 0
):
    server = Meta.meta.getServer(server_id)
    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    _, updated_groups, _ = set_channel_acls(server, channel_id, groups)

    output = []
    for g in updated_groups:
        output.append({
            "name": g.name,
            "users": g.add
        })

    return 200, {
        "channel_id": channel_id,
        "results": output
    }


@api.get(
    "/auth/groups",
    response={
        200: dict,
        404: dict,
    },
    tags=["Auth"]
)
def get_auth_update_groups(
    request,
    server_id: int = 0,
    channel_id: int = 0
):
    server = Meta.meta.getServer(server_id)
    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    _, groups, _ = get_channel_acls(server, channel_id)

    output = []
    for g in groups:
        output.append({
            "name": g.name,
            "users": g.add
        })

    return 200, {
        "channel_id": channel_id,
        "new_groups": output
    }


@api.delete(
    "auth/users/delete",
    response={
        200: dict,
        404: dict,
    },
    tags=["Auth"]
)
def delete_user_id(
    request,
    server_id: int,
    user_id: int,
):
    """
        Delete user from server
    """
    server = Meta.meta.getServer(server_id)

    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    user = get_registered_user(server, user_id)
    if not user:
        return 404, {"error": "User Not Found"}

    unregister_user(server, user_id)

    return 200, {
        "user_id": user_id,
        "kicked": 'Success'
    }


@api.delete(
    "auth/users/kick",
    response={
        200: dict,
        404: dict,
    },
    tags=["Active"]
)
def delete_users_kick(request, server_id: int, user_name: str = "", reason: str = "Auth Revoked"):
    """
        Kick user on server
    """
    server = Meta.meta.getServer(server_id)

    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    user = get_active_username(server, user_name)
    if not user:
        return 404, {"error": "User Not Found"}

    server.kickUser(user.get("session"), reason)

    return 200, {
        "user_id": user.get("userid"),
        "kicked": 'Success'
    }

@api.get(
    "/servers/{server_id}/user_list",
    response={
        200: list[dict],
        404: dict,
    },
    tags=["Server"]
)
def get_server_server_id(request, server_id: int,):
    """
    Lists servers registered users
    """

    server = Meta.meta.getServer(server_id)

    # Return 404 if not found
    if server is None:
        return 404, {"error": "Server Not Found"}

    out = []
    users = server.getRegisteredUsers('') if server.isRunning() else []
    for u in users:
        _u = obj_to_dict(server.getRegistration(u))
        out.append(_u)
    return out


# @api.delete(
#     "/servers/{server_id}/delete",
#     response={
#         200: str,
#         404: dict,
#     },
#     tags=["Server"]
# )
# def delete_server_server_id(request, server_id: int,):
#     """
#     Deletes a server
#     """
#     if request.user.is_superuser:
#         if server_id<2:
#             return "NO"

#         server = Meta.meta.getServer(server_id)

#         # Return 404 if not found
#         if server is None:
#             return 404, {"error": "Server Not Found"}
#         server.stop()
#         return str(server.delete())


# @api.get(
#     "/servers/new",
#     response={
#         200: dict,
#         404: dict,
#     },
#     tags=["Server"]
# )
# def new_server(request, user_count="100", motd="Welcome to this 'Private' Mumble.\n\nLog in Pew, Die reship, REPEAT!!"):
#     """
#     Lists servers registered users
#     """
#     if request.user.is_superuser:
#         s = Meta.meta.newServer()

#         # Return 404 if not found
#         if s is None:
#             return 404, {"error": "Server Not Found"}
    
#         s.setConf("users", user_count)
#         s.setConf("welcometext", motd)
#         s.setConf("password", ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)))
#         s.start()

#         return {
#             'id': s.id(),
#             'name': get_server_conf(Meta.meta, s, 'registername'),
#             'host': get_server_conf(Meta.meta, s, 'host'),
#             'port': get_server_port(Meta.meta, s),
#             'password': get_server_conf(Meta.meta, s, 'password'),
#             'welcometext': get_server_conf(Meta.meta, s, 'welcometext'),
#             'maxusers': get_server_conf(Meta.meta, s, 'users') or 0,
#             'running': s.isRunning(),
#         }


@api.get(
    "/servers/{server_id}/channels/export",
    response={200: dict, 404: dict},
    tags=["Channels"]
)
def get_channel_export(request, server_id: int):
    """
    Export all channels and their ACL groups as JSON.
    Temporary channels are excluded.
    """
    server = Meta.meta.getServer(server_id)
    if server is None:
        return 404, {"error": "Server Not Found"}
    channels = export_channels(server)
    return 200, {"server_id": server_id, "channels": channels}


@api.post(
    "/servers/{server_id}/channels/import",
    response={200: dict, 404: dict},
    tags=["Channels"]
)
def post_channel_import(request, server_id: int, body: ChannelImportRequest):
    """
    Overwrite all channels on the server with the provided config.
    All existing non-root channels are deleted first.
    Groups referencing unknown user IDs are silently filtered.
    """
    server = Meta.meta.getServer(server_id)
    if server is None:
        return 404, {"error": "Server Not Found"}
    id_map = import_channels(server, body.channels)
    return 200, {"server_id": server_id, "channels_created": len(id_map) - 1}


# ServerEndpoints(api)

if settings.DEBUG and False:
    UserEndpoints(api)
    ACLEndpoints(api)
    ActiveEndpoints(api)
