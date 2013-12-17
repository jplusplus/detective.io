from app.detective.register import init_topics
import sys
# -*- coding: utf-8 -*-
class Wrapper(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        init_topics()

    def __getattr__(self, name):
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            print "noob"

sys.modules[__name__] = Wrapper( sys.modules[__name__] )