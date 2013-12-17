import re
from django.http          import Http404
from app.detective        import topics
from app.detective.models import Topic

class VirtualApi:
    def process_request(self, request):
        regex = re.compile(r'api/([a-zA-Z0-9_\-]+)/')
        urlparts = regex.findall(request.path)
        if urlparts:
            # Get the topic that match to this url.
            try:
                topic = Topic.objects.get(slug=urlparts[0])
                # This will automaticly create the API if needed
                # or failed if the topic is unknown
                try:
                    getattr(topics, topic.module)
                except AttributeError as e:
                    raise Http404(e)
            except Topic.DoesNotExist:
                raise Http404()

        return None
