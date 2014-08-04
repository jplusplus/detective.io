from django.db.models           import signals
from app.detective.utils        import topic_cache, get_topic_from_model
from app.detective.models       import Topic
from app.detective.permissions  import create_permissions, remove_permissions

def update_permissions(*args, **kwargs):
    """ create the permissions related to the label module """
    assert kwargs.get('instance')
    # @TODO check that the slug changed or not to avoid permissions hijacking
    if kwargs.get('created', False):
        create_permissions(kwargs.get('instance').get_module(), app_label=kwargs.get('instance').ontology_as_mod)

def update_topic_cache(*args, **kwargs):
    """ update the topic cache version on topic update or sub-model update """
    instance = kwargs.get('instance')
    if not isinstance(instance, Topic):
        topic = get_topic_from_model(instance)
    else:
        topic = instance
    # we increment the cache version of this topic, this will "invalidate" every
    # previously stored information related to this topic
    topic_cache.incr_version(topic)

    # if topic just been created we gonna bind its sub models signals
    if kwargs.get('created'):
        for Model in topic.get_models():
            signals.post_save.connect(update_topic_cache, sender=Model, weak=False )


def remove_topic_cache(*args, **kwargs):
    topic_cache.delete_version(kwargs.get('instance'))

def bind():
    signals.post_save.connect(update_topic_cache,   sender=Topic)
    signals.post_save.connect(update_permissions,   sender=Topic)
    signals.pre_delete.connect(remove_topic_cache,  sender=Topic)
    signals.post_delete.connect(remove_permissions, sender=Topic)


