
from ..mumble_ice import Meta
from .utils import STD_RESPONSES, ACLGroup, set_channel_acls, get_channel_acls

class ACLEndpoints():
    def __init__(self, api):


        @api.get(
            "server/{server_id}/ch/{channel_id}/acl",
            response=STD_RESPONSES,
            tags=["ACL"]
        )
        def get_server_channel_acl(
            request,
            server_id: int,
            channel_id: int
        ):
            """
                get acl groups
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            acl, groups, inherit = get_channel_acls(server, channel_id)

            return 200, {
                "user_id": channel_id,
                "updated": 'Success'
            }

        @api.post(
            "server/{server_id}/ch/{channel_id}/acl",
            response=STD_RESPONSES,
            tags=["ACL"]
        )
        def post_server_channel_acl(
            request,
            server_id: int,
            channel_id: int,
            groups: list[ACLGroup]
        ):
            """
                Update acl groups
            """
            server = Meta.meta.getServer(server_id)

            # Return 404 if not found
            if server is None:
                return 404, "Server Not Found"
            
            set_channel_acls(server, channel_id, groups)

            return 200, {
                "user_id": channel_id,
                "updated": 'Success'
            }
