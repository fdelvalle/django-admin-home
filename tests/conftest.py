"""Installs the package on the default admin site before any test runs.

``install()`` patches ``AdminSite.get_urls``, and ``tests/urls.py`` freezes
``admin.site.urls`` into a plain list the first time it's imported (Django
resolves ``ROOT_URLCONF`` lazily, on first URL resolution). Calling
``install()`` here, at conftest import time — which always happens before
any test triggers URL resolution — guarantees the custom
toggle-favorite/track-access routes are present in that frozen list.
"""

import django_admin_home

django_admin_home.install()
