from datetime import timedelta
from django.shortcuts import render
from django.conf import settings

from django.views.decorators.cache import cache_page

from .mumble_ice import Meta
from .api.utils import get_server_conf, get_server_port

# @cache_page(30)
def index(request):
    server = None
    servers = []
    if request.user.is_authenticated:
        try:
            for s in Meta.meta.getAllServers():
                port = get_server_port(Meta.meta, s)
                is_running = s.isRunning()
                uptime = s.getUptime() if is_running else 0
                servers.append({
                    'id': s.id(),
                    'port': port,
                    'running': is_running,
                    'users': (is_running and len(s.getUsers())) or 0,
                    'maxusers': get_server_conf(Meta.meta, s, 'users') or 0,
                    'channels': (is_running and len(s.getChannels())) or 0,
                    'uptime_seconds': uptime if is_running else 0,
                    'uptime': str(
                        timedelta(seconds=uptime) if is_running else ''
                    ),
                })
        except:
            pass
    try:
        s = Meta.meta.getVersion()
        ut = Meta.meta.getUptime()
        server = {
            "up": ut,
            "version": s[3],
        }
    except Exception as e: 
        pass
    context = {
        "host": "mumble.sh1t.space",
        "debug": settings.DEBUG,
        "server": server,
        "servers": servers
    }

    return render(request, 'mumble_rest/index.html', context=context)
