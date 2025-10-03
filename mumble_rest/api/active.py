from datetime import timedelta

from ninja import Form
from ..mumble_ice import Meta, MumbleServer
from .utils import STD_RESPONSES, check_user_pass, get_channel_acls, get_registered_user_id, get_registered_users, get_server_conf, get_server_port, obj_to_dict, register_user, unregister_user, update_user_pass
from django.utils import timezone

class ActiveEndpoints():
    def __init__(self, api):

        @api.get(
            "server/{server_id}/active_users",
            response=STD_RESPONSES,
            tags=["Active"]
        )
        def get_users(request, server_id: int):
            """
                Gets all users on server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"

            data = obj_to_dict(server.getUsers())

            return 200, data

        @api.get(
            "server/{server_id}/active_users",
            response=STD_RESPONSES,
            tags=["Active"]
        )
        def get_user(request, server_id: int, user_name: str = ""):
            # TODO: This is really non-scalable as the number of users on the server grows
            #       Find a better way to get a user by userid from mumble
            res, users = get_users(request, server_id)
            for u in users.values():
                if u.get("userName") == user_name:
                    return 200, u
            return 404, "Not found"

        @api.post(
            "server/{server_id}/active_users/mute",
            response=STD_RESPONSES,
            tags=["Active"]
        )
        def post_users_mute(request, server_id: int, user_name: str = ""):
            """
                Mute user on server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"

            res, user = get_user(request, server_id, user_name)
            if res != 200:
                return 404, "User Not Found"

            state = server.getState(user.get("session"))
            state.mute = True
            state.suppress = True

            server.setState(state)

            return 200, {
                "user_id": user.get("userid"),
                "muted": 'Success'
            }
        
        @api.post(
            "server/{server_id}/active_users/unmute",
            response=STD_RESPONSES,
            tags=["Active"]
        )
        def post_users_unmute(
            request,
            server_id: int,
            user_name: Form[str] = ""
        ):
            """
                Unmute user on server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"

            res, user = get_user(request, server_id, user_name)
            if res != 200:
                return 404, "User Not Found"

            state = server.getState(user.get("session"))
            state.mute = False
            state.suppress = False

            server.setState(state)

            return 200, {
                "user_id": user.get("userid"),
                "muted": 'Success'
            }

        @api.delete(
            "server/{server_id}/active_users/kick",
            response=STD_RESPONSES,
            tags=["Active"]
        )
        def delete_users_kick(request, server_id: int, user_name: str ="", reason: str=""):
            """
                Kick user on server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"

            res, user = get_user(request, server_id, user_name)
            if res != 200:
                return 404, "User Not Found"

            server.kickUser(user.get("session"), reason)
            
            return 200, {
                "user_id": user.get("userid"),
                "kicked": 'Success'
            }
        