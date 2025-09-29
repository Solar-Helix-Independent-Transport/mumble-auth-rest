from typing import Any, Optional
from django.http import HttpRequest
from django.conf import settings
from ..mumble_ice import Meta
from ninja.security import django_auth
from ninja import Form, NinjaAPI
from .servers import ServerEndpoints
from .users import UserEndpoints
from .acls import ACLEndpoints
from .utils import ACLGroup, check_user_pass, get_channel_acls, get_registered_user_id, register_user, set_channel_acls, update_user_pass
from ninja.security import APIKeyQuery
from mumble_rest.models import APIKey

class check_api_key(APIKeyQuery):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        test = False
        for t in APIKey.objects.all():
            _t = t.test(key)
            if _t:
                test = True
                break
        return test


api = NinjaAPI(
    title="Mumble Rest",
    auth=[
        check_api_key()
    ]
)


@api.get(
    "/health-check",
    tags=["Status"])
def get_status(request):
    """
        Mumble Health Check
    """
    try:
        s = Meta.meta.getVersion()
        ut = Meta.meta.getUptime()
        return 200, {'status': 'OK', "version": s, "uptime": ut}
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


if settings.DEBUG and False:
    ServerEndpoints(api)
    UserEndpoints(api)
    ACLEndpoints(api)
