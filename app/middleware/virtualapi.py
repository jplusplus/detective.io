from django.http          import Http404
from app.detective        import topics
from app.detective.models import Topic
from app.detective.utils  import get_topic_from_request
import re

class VirtualApi:
    def process_request(self, request):
        regex = re.compile(r'api/([a-zA-Z0-9_\-.]+)/([a-zA-Z0-9_\-]+)/')
        urlparts = regex.findall(request.path)

        if urlparts:
            # Get the topic that match to this url.
            topic = get_topic_from_request(request)
            if topic == None:
                raise Http404(Topic.DoesNotExist())
            else:
                # This will automaticly create the API if needed
                # or failed if the topic is unknown
                try:
                    getattr(topics, topic.ontology_as_mod)
                except AttributeError as e:
                    raise Http404(e)

        return None
