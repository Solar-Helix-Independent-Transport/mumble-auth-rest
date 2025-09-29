from datetime import timedelta
from ..mumble_ice import Meta
from .utils import get_server_conf, get_server_port, obj_to_dict


class ServerEndpoints:
    def __init__(self, api):
        
        @api.get(
            "/servers",
            tags=["Server"]
        )
        def get_servers(request):
            """
            List all Servers
            """
            servers = []
            for s in Meta.meta.getAllServers():
                host = get_server_conf(Meta.meta, s, 'host')
                port = get_server_port(Meta.meta, s)
                is_running = s.isRunning()
                uptime = s.getUptime() if is_running else 0

                servers.append({
                    'id': s.id(),
                    'name': get_server_conf(Meta.meta, s, 'registername'),
                    'address': '%s:%s' % (host, port),
                    'host': host,
                    'port': port,
                    'running': is_running,
                    'users': (is_running and len(s.getUsers())) or 0,
                    'maxusers': get_server_conf(Meta.meta, s, 'users') or 0,
                    'channels': (is_running and len(s.getChannels())) or 0,
                    'uptime_seconds': uptime if is_running else 0,
                    'uptime': str(
                        timedelta(seconds=uptime) if is_running else ''
                    ),
                    'log_length': s.getLogLen()
                })

            return servers

        @api.get(
            "/servers/{server_id}/",
            tags=["Server"]
        )
        def get_server_server_id(request, server_id):
            """
            Lists server details
            """

            id = int(server_id)
            s = Meta.meta.getServer(id)

            # Return 404 if not found
            if s is None:
                return 404, "Not Found"

            tree = obj_to_dict(s.getTree()) if s.isRunning() else None

            json_data = {
                'id': s.id(),
                'name': get_server_conf(Meta.meta, s, 'registername'),
                'host': get_server_conf(Meta.meta, s, 'host'),
                'port': get_server_port(Meta.meta, s),
                'address': '%s:%s' % (
                    get_server_conf(Meta.meta, s, 'host'),
                    get_server_port(Meta.meta, s),
                ),
                'password': get_server_conf(Meta.meta, s, 'password'),
                'welcometext': get_server_conf(Meta.meta, s, 'welcometext'),
                'user_count': (s.isRunning() and len(s.getUsers())) or 0,
                'maxusers': get_server_conf(Meta.meta, s, 'users') or 0,
                'running': s.isRunning(),
                'uptime': s.getUptime() if s.isRunning() else 0,
                'humanize_uptime': str(
                    timedelta(seconds=s.getUptime()) if s.isRunning() else ''
                ),
                'parent_channel': tree['c'] if s.isRunning() else None,
                'sub_channels': tree['children'] if s.isRunning() else None,
                'users': tree['users'] if s.isRunning() else None,
                'registered_users': s.getRegisteredUsers('') if s.isRunning() else None,
                'log_length': s.getLogLen()
            }

            return json_data

