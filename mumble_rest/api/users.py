from ninja import Form
from ..mumble_ice import Meta
from .utils import STD_RESPONSES, check_user_pass, get_channel_acls, get_registered_user, get_registered_user_id, get_registered_users, get_server_conf, get_server_port, obj_to_dict, register_user, unregister_user, update_user_pass

class UserEndpoints():
    def __init__(self, api):

        @api.post(
            "server/{server_id}/users/register",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def post_user_register(
            request,
            server_id: int,
            user_name: Form[str],
            user_pass: Form[str]
        ):
            """
                register user on server and return the UID
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            if get_registered_user_id(server, user_name):
                return 404, "User Exists"

            uid = register_user(server, user_name)
            update_user_pass(server, user_name, user_pass)
            test = check_user_pass(server, user_name, user_pass)

            return 200, {
                "user_id": uid,
                "password_test": test,
            }

        @api.post(
            "server/{server_id}/users/test",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def post_test_user_pass(
            request,
            server_id: int,
            user_name: Form[str],
            user_pass: Form[str]
        ):
            """
                register user on server and return the UID
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            test = check_user_pass(server, user_name, user_pass)

            return 200, {
                "user_id": user_name,
                "password_test": test,
            }

        @api.delete(
            "server/{server_id}/user/",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def delete_user_name(
            request,
            server_id: int,
            user_name: str,
        ):
            """
                Delete user from server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            user_id = get_registered_user_id(server, user_name)
            if not user_id:
                return 404, "User Not Found"
            
            unregister_user(user_id)

            return 200, {
                "user_id": user_id,
                "kicked": 'Success'
            }

        @api.delete(
            "server/{server_id}/user/{user_id}/",
            response=STD_RESPONSES,
            tags=["Users"]
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
                return 404, "Server Not Found"
            
            user_id = get_registered_user(server, user_id)
            if not user_id:
                return 404, "User Not Found"
            
            #unregister_user(user_id)

            return 200, {
                "user_id": user_id,
                "kicked": 'Success'
            }

        @api.get(
            "server/{server_id}/users/",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def get_user_registration(
            request,
            server_id: int,
            user_name: Form[str],
        ):
            """
                Kick user on server
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            user = get_registered_user_id(server, user_name)

            if not user:
                return 404, "User Not Found"
            
            return 200, obj_to_dict(user)
       
        @api.post(
            "server/{server_id}/users/change_pass",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def post_user_update_pw(
            request,
            server_id: int,
            user_name: Form[str],
            user_pass: Form[str]
        ):
            """
                update user PW
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            uid = get_registered_user_id(server, user_name)

            if not uid:
                return 404, "User Not Found"
            
            update_user_pass(server, user_name, user_pass)
            test = check_user_pass(server, user_name, user_pass)
            return 200, {
                "user_id": uid,
                "password_test": test,
                "updated": 'Success'
            }

        @api.get(
            "server/{server_id}/ch/{channel_id}/acl",
            response=STD_RESPONSES,
            tags=["Users"]
        )
        def get_server_channel_acl(
            request,
            server_id: int,
            channel_id: int
        ):
            """
                Update user groups
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            acl, groups, inherit = get_channel_acls(server, channel_id)

            return 200, {
                "user_id": cacl,
                "updated": 'Success'
            }
