## Mumble-Auth-Rest

### Overview

Mumble-Auth-REST is a RESTful web application wrapper over the Murmur SLICE API to auth users form Alliance Auth.

This project is heavily based on [Murmur-Rest](https://github.com/alfg/murmur-rest)

## Setup
1. clone repo
1. create and enter a venv `python3 -m venv .venv` `source .venv/bin/activate`
1. install deps `pip install -r requirements.txt`
1. rename `mumble-rest/settings.py.example` to `mumble-rest/settings.py`
1. update `mumble-rest/settings.py` to your liking
   - ice access key
   - urls and allowed hosts
   - etc... 
1. create database `python manage.py migrate`
1. create su `python manage.py createsuperuser`
1. run server `python manage.py runserver localhost:8008`

##  Deployment for Production

Following the same steps for Deployment for Development, just use a Python WSGI application server
such as [Gunicorn](http://gunicorn.org/) instead of the built-in Flask server. The provided `wsgi.py`
file is provided for this.

For example, if using Gunicorn and virtualenv:

```
/path/to/mumble-rest/env/bin/gunicorn -b 127.0.0.1:8008 wsgi:app
```

### Cloudflaird and nginx statics
```conf
server { # Listen for incoming HTTP requests on port 80.
    listen 8000;
    server_name localhost; # local host only.

    location /static { # Static files need to be here make sure perms are good.
        alias /var/www/mumblerest/static; 
        autoindex off;
    }

    location / { # else goto the gunicorn instance.
        proxy_pass http://localhost:8008; # Forward requests to your backend server.
        proxy_set_header Host $host; # Pass the original Host header.
        proxy_set_header X-Real-IP $remote_addr; # Pass the client's real IP address.
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # Pass a list of IP addresses the request has traversed.
        proxy_set_header X-Forwarded-Proto $scheme; # Pass the original protocol (HTTP or HTTPS).
    }
}
```

### SSH Tunnels vs Public API
You do not need to expose this API publically if you don't want to you can simple run an ssh tunnel between the 2 servers and hit it that way.

## TODO
- Better Error Handling
- Tests

### Resources
- [Mumble SLICE API](https://www.mumble.info/documentation/slice/1.3.0/html/_sindex.html)
- [Mumbleverse](https://github.com/Solar-Helix-Independent-Transport/allianceauth-mumble-multiverse)

### License

The MIT License (MIT)

Copyright (c) 2016 github.com/pvyParts

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
