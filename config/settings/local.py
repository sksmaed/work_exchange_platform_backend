from config.settings.base import *  # noqa: F403
from config.settings.base import env

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[".localhost", "127.0.0.1", "[::1]", "localhost:3000"],
)

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:8081",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
)

if DEBUG:  # noqa: F405
    INSTALLED_APPS += [  # noqa: F405
        "debug_toolbar",
        "query_inspector",
    ]
    MIDDLEWARE += [  # noqa: F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "query_inspector.middleware.QueryCountMiddleware",
    ]
    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": [
            "debug_toolbar.panels.profiling.ProfilingPanel",
            "debug_toolbar.panels.redirects.RedirectsPanel",
        ],
        "SHOW_TEMPLATE_CONTEXT": True,
    }
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

CACHES["default"]["LOCATION"] = env("CACHES_URL", default="valkey://127.0.0.1:6379/0")  # noqa: F405
