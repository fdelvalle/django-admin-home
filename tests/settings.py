"""Minimal Django settings module used by pytest-django to run the test suite."""

DEBUG = True
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["testserver", "example.com"]

INSTALLED_APPS = [
    # Both before django.contrib.admin so django_admin_home's bundled
    # admin/index.html + admin/nav_sidebar.html, and testapp's
    # admin/base_site.html (which wires up the user menu, standing in for
    # a host project), override the default ones via the app_directories
    # template loader.
    "django_admin_home",
    "tests.testapp",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_admin_home.context_processors.admin_user",
                "django_admin_home.context_processors.admin_languages",
            ],
        },
    }
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STATIC_URL = "/static/"
USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("pt-br", "Portuguese (Brazil)")]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "tests.urls"
