#!/usr/bin/env python
# Encoding: utf-8

from django.http import HttpResponse
from django.conf import settings
import json 

class JsonAsHTML(object):
    '''
    View a JSON response in your browser as HTML
    Useful for viewing stats using Django Debug Toolbar 

    This middleware should be place AFTER Django Debug Toolbar middleware   
    '''

    def process_response(self, request, response):
        in_debug = request.GET.get('debug', None)
        #not for production or production like environment 
        if not settings.DEBUG or not in_debug:
            return response

        #do nothing for actual ajax requests
        elif request.is_ajax():
            return response

        #only do something if this is a json response
        elif "application/json" in response['Content-Type'].lower():
            title = "JSON as HTML Middleware for: %s" % request.get_full_path()
            response.content = u"<html><head><title>%s</title></head><body>%s</body></html>" % (title, response.content.decode('utf-8'))
            response['Content-Type'] = 'text/html'
        return response