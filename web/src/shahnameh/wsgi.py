"""
WSGI config for shahnameh project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import signal

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

import client.grpc_client


def close_channel():
    try:
        client.grpc_client.GrpcClient().destroy_channel()
    except:
        print('GRPC channel already closed')


signal.signal(signal.SIGINT, close_channel)
signal.signal(signal.SIGTerm, close_channel)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shahnameh.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)
application.add_files(settings.STATIC_ROOT, prefix=settings.STATIC_URL)
