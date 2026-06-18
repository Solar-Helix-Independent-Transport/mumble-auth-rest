import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumble_rest.settings_docker")

import django
django.setup()

from mumble_rest.models import APIKey, generate_token

k = generate_token()
APIKey.objects.create(name="ci", token=k)
print(k, end="", flush=True)
