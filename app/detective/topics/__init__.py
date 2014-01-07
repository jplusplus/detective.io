# -*- coding: utf-8 -*-
from app.detective.models   import Topic
from app.detective.register import topic_models
import sys

class Wrapper:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            try:
                path = __package__ + "." + name
                # Create the topic using its models
                return topic_models(path)
            except Topic.DoesNotExist:
                # Raise a basic attribute error
                raise AttributeError("The attribute '%s' doesn't exist." % name)

sys.modules[__name__] = Wrapper( sys.modules[__name__] )
