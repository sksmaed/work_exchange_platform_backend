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
    ],
)

if DEBUG:  # noqa: F405
    try:
        import debug_toolbar  # noqa: F401
        INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
        MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
    except ImportError:
        pass

    try:
        import query_inspector  # noqa: F401
        INSTALLED_APPS += ["query_inspector"]  # noqa: F405
        MIDDLEWARE += ["query_inspector.middleware.QueryCountMiddleware"]  # noqa: F405
    except ImportError:
        pass
    DEBUG_TOOLBAR_CONFIG = {
        "DISABLE_PANELS": [
            "debug_toolbar.panels.profiling.ProfilingPanel",
            "debug_toolbar.panels.redirects.RedirectsPanel",
        ],
        "SHOW_TEMPLATE_CONTEXT": True,
    }
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

CACHES["default"]["LOCATION"] = env("CACHES_URL", default="valkey://127.0.0.1:6379/0")  # noqa: F405

# Override cache for tests to use dummy backend
import sys  # noqa: E402
if "pytest" in sys.modules or "pytest" in sys.argv[0]:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }