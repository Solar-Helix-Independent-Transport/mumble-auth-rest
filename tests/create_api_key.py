import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumble_rest.settings_docker")

import django
django.setup()

from django.core.management import call_command
call_command('migrate', verbosity=0, fake_initial=True)

from mumble_rest.models import APIKey, generate_token

k = generate_token()
APIKey.objects.create(name="ci", token=k)
print(k, end="", flush=True)
