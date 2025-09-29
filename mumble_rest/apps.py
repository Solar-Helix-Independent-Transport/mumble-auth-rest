from django.apps import AppConfig

from . import __version__

class MumbleRestConfig(AppConfig):
    name = "mumble_rest"
    label = "mumble_rest"
    verbose_name = f"Mumble Rest v{__version__}"

