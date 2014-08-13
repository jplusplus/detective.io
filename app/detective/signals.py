from django.db.models           import signals
from django.contrib.auth        import get_user_model
from django.db.utils            import DatabaseError
from app.detective.utils        import topic_cache, get_topic_from_model
from app.detective.models       import Topic, DetectiveProfileUser
from app.detective.permissions  import create_permissions, remove_permissions

User = get_user_model()


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
        try:
            topic = get_topic_from_model(instance)
        except Topic.DoesNotExist:
            topic = None
    else:
        topic = instance

    if topic:
        # we increment the cache version of this topic, this will "invalidate" every
        # previously stored information related to this topic
        topic_cache.incr_version(topic)

        # if topic just been created we gonna bind its sub models signals
        if kwargs.get('created'):
            bind_topic_models(topic)

def remove_topic_cache(*args, **kwargs):
    topic_cache.delete_version(kwargs.get('instance'))

def bind_topic_models(topic):
    for Model in topic.get_models():
        signals.post_save.connect(update_topic_cache, sender=Model, weak=False )

def user_created(*args, **kwargs):
    """

    create a DetectiveProfileUser when a user is created

    """
    DetectiveProfileUser.objects.get_or_create(user=kwargs.get('instance'))


def bind():
    signals.post_save.connect(user_created,         sender=User)
    signals.post_save.connect(update_topic_cache,   sender=Topic)
    signals.post_save.connect(update_permissions,   sender=Topic)
    signals.pre_delete.connect(remove_topic_cache,  sender=Topic)
    signals.post_delete.connect(remove_permissions, sender=Topic)

    try:
        # for existing topics we need to bind their submodels
        for topic in Topic.objects.all():
            bind_topic_models(topic)
    except DatabaseError:
        pass



