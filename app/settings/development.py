from .common import *

MIDDLEWARE_CLASSES.append( 'debug_toolbar.middleware.DebugToolbarMiddleware')
MIDDLEWARE_CLASSES.append( 'app.middleware.debug_toolbar.JsonAsHTML')

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', '::1')
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'neo4j_panel.Neo4jPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
)
INSTALLED_APPS += ('debug_toolbar',)
USE_DEBUG_TOOLBAR = True

ENABLE_PROFILING = False