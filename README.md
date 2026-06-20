# Mumble-Auth-REST

A RESTful API wrapper over the Murmur ICE API, designed to integrate Mumble with [Alliance Auth](https://github.com/allianceauth/allianceauth) via the [Mumbleverse](https://github.com/Solar-Helix-Independent-Transport/allianceauth-mumble-multiverse) plugin.

Heavily based on [Murmur-Rest](https://github.com/alfg/murmur-rest).

---

## Docker Deployment (Recommended)

The recommended way to run mumble-rest is alongside a Mumble server using Docker Compose, integrated into your existing AllianceAuth stack.

### 1. Copy the env file and fill in values

```bash
cp .env-mumble.example .env-mumble
```

Edit `.env-mumble`:

```env
MUMBLE_SUPERUSER_PASSWORD=changeme       # Mumble server superuser password
MUMBLE_SERVER_PASSWORD=                  # Leave blank for an open server
MUMBLE_ICE_SECRET=changeme              # Shared secret between Mumble and mumble-rest
MUMBLE_REST_SECRET_KEY=changeme         # Long random string — Django secret key
```

### 2. Add the services to your AllianceAuth docker-compose

Copy the contents of `docker-compose.example.yml` into your existing `docker-compose.yml`. It adds two services: `mumble` and `mumble_rest`.

The `mumble_rest` service communicates with the Mumble server over Ice internally (`mumble:6502`) and is not exposed publicly — AllianceAuth reaches it via the internal Docker network (`http://mumble_rest:8000`).

### 3. Start the services

```bash
docker compose up -d mumble mumble_rest
```

### 4. Create an API key

Open the Django admin for mumble-rest:

```
http://<your-host>/mumble-rest/admin/
```

> If mumble-rest shares a host with AllianceAuth, you can expose the admin via a separate nginx location or port. The admin is only accessible to Django staff users.

Navigate to **Mumble Rest → API Keys → Add**. Copy the key before saving — it is hashed on save and cannot be retrieved afterwards.

Alternatively, create a key from the command line:

```bash
docker compose exec mumble_rest python manage.py shell -c "
from mumble_rest.models import APIKey, generate_token
k = generate_token()
APIKey.objects.create(name='allianceauth', token=k)
print(k)
"
```

### 5. Configure AllianceAuth

See the [AllianceAuth Integration](#allianceauth-integration-mumbleverse) section below.

### API docs

Interactive API docs (requires Django staff login) are available at:

```
http://mumble_rest:8000/api/docs
```

---

## AllianceAuth Integration (Mumbleverse)

[allianceauth-mumble-multiverse](https://github.com/Solar-Helix-Independent-Transport/allianceauth-mumble-multiverse) is the AllianceAuth plugin that connects to mumble-rest. It supports multiple Mumble servers from a single Auth install, each with independent access control.

### Install

In your AllianceAuth `conf/requirements.txt`:

```
allianceauth-mumble-multiverse
```

In `conf/local.py`:

```python
INSTALLED_APPS += [
    'mumbleverse',
]
```

Run migrations and restart AllianceAuth after adding the app.

### Register a server

In the AllianceAuth admin, go to **Mumbleverse → Mumbleverse servers → Add**:

| Field | Description |
|---|---|
| Name | Display name shown to users |
| mumble_url | Public address for Mumble clients, e.g. `mumble.your-domain.com:64738` |
| mumble_virtual_server_id | Murmur virtual server ID (almost always `1`) |
| api_url | Internal URL of mumble-rest, e.g. `http://mumble_rest:8000` |
| api_key | The API key you created in mumble-rest |
| Active | Uncheck to disable without deleting |

> **Note:** AllianceAuth must be restarted after adding or removing a server. The service hooks are registered at startup.

### Access control

Each server has independent access control. A user can see a server if they match **any** of the following:

| Field | Grants access to |
|---|---|
| state_access | All users in the selected AllianceAuth states |
| group_access | All users in the selected groups |
| character_access | Specific EVE characters |
| corporation_access | All members of the selected corporations |
| alliance_access | All members of the selected alliances |
| faction_access | All members of the selected factions |

Users with the `mumbleverse.global_access` permission can see all servers regardless of these filters.

### Permissions

| Permission | Effect |
|---|---|
| `mumbleverse.basic_access` | Required to see any Mumble servers at all |
| `mumbleverse.global_access` | Can see all servers, bypassing per-server access control |

### Username format

Mumble usernames are formatted as `[{corp_ticker}] {character_name}` using the user's main character. This is set by the `name_format` on the `MumbleverseService` hook.

### Smart filters

Mumbleverse registers a secure group filter: **Smart Filter: Mumbleverse Server Active**. This lets you gate AllianceAuth group membership on whether a user has an active account on a specific Mumble server. An optional `reversed_logic` flag flips the check to pass users who do *not* have an account.

---

## Manual / Development Setup

For local development or non-Docker deployments.

### Prerequisites

- Python 3.12+
- A running Mumble/Murmur server with Ice enabled

### Steps

```bash
git clone <repo>
cd mumble-rest
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp mumble_rest/settings.py.example mumble_rest/settings.py
```

Edit `mumble_rest/settings.py` and set:
- `SECRET_KEY` — a long random string
- `ALLOWED_HOSTS` — your hostname(s)
- `ICE_HOST_HOST` / `ICE_HOST_PORT` — where your Murmur Ice interface listens
- `ICE_SECRET` — your Murmur Ice secret

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver localhost:8008
```

Create an API key in the admin at `http://localhost:8008/admin/`.

### Production (bare-metal)

Use [Gunicorn](https://gunicorn.org/) instead of the dev server:

```bash
.venv/bin/gunicorn mumble_rest.wsgi:application --bind 127.0.0.1:8008 --workers 2
```

Nginx config to proxy in front of Gunicorn:

```nginx
server {
    listen 8000;
    server_name localhost;

    location /static {
        alias /var/www/mumblerest/static;
        autoindex off;
    }

    location / {
        proxy_pass http://127.0.0.1:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> You do not need to expose this API publicly. An SSH tunnel between the AllianceAuth server and the Mumble server works fine.

---

## Resources

- [Mumble SLICE API](https://www.mumble.info/documentation/slice/1.3.0/html/_sindex.html)
- [Mumbleverse plugin](https://github.com/Solar-Helix-Independent-Transport/allianceauth-mumble-multiverse)

## License

MIT — Copyright (c) 2016 github.com/pvyParts
