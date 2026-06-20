import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumble_rest.settings_docker")

import django
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

executor = MigrationExecutor(connection)
if executor.migration_plan(executor.loader.graph.leaf_nodes()):
    call_command('migrate', verbosity=0)

from mumble_rest.models import APIKey, generate_token

k = generate_token()
APIKey.objects.create(name="ci", token=k)
print(k, end="", flush=True)
