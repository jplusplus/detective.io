from django.db.models           import signals
from app.detective              import utils
from app.detective.models       import Topic
from app.detective.permissions  import create_permissions, remove_permissions
def update_permissions(*args, **kwargs):
    """ create the permissions related to the label module """
    assert kwargs.get('instance')
    # @TODO check that the slug changed or not to avoid permissions hijacking
    if kwargs.get('created', False):
        create_permissions(kwargs.get('instance').get_module(), app_label=kwargs.get('instance').ontology_as_mod)

def update_topic_cache(*args, **kwargs):
    utils.topic_cache.incr_version(kwargs.get('instance'))


def bind():
    signals.post_save.connect(update_topic_cache,   sender=Topic)
    signals.post_delete.connect(remove_permissions, sender=Topic)
    signals.post_save.connect(update_permissions,   sender=Topic)