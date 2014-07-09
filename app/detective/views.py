#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http      import Http404, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template  import TemplateDoesNotExist, RequestContext
from django.conf      import settings
import urllib2
import mimetypes

def home(request):
    # Render template without any argument
    response = render_to_response('home.dj.html', context_instance=RequestContext(request))

    # Add a cookie containing some user information
    if request.user.is_authenticated():
        permissions = request.user.get_all_permissions()
        # Create the cookie
        response.set_cookie("user__is_logged",   1)
        response.set_cookie("user__is_staff",    1*request.user.is_staff)
        response.set_cookie("user__username",    unicode(request.user.username))
    else:
        # Deletre existing cookie
        response.delete_cookie("user__is_logged")
        response.delete_cookie("user__is_staff")
        response.delete_cookie("user__username")

    return response

def partial(request, partial_name=None):
    template_name = 'partials/' + partial_name + '.dj.html'
    try:
        return render_to_response(template_name)
    except TemplateDoesNotExist:
        raise Http404

def partial_explore(request, topic=None):
    template_name = 'partials/topic.explore.' + topic + '.dj.html'
    try:
        return render_to_response(template_name)
    except TemplateDoesNotExist:
        return partial(request, partial_name='topic.explore.common')

def not_found(request):
    return redirect("/404/")

def proxy(request, name=None):
    if settings.STATIC_URL[0] == '/':
        return redirect('%s%s' %(settings.STATIC_URL, name));
    else:
        url = '%s%s' % (settings.STATIC_URL, name)
        try :
            proxied = urllib2.urlopen(url)
            status_code = proxied.code
            mimetype = proxied.headers.typeheader or mimetypes.guess_type(url)
            content = proxied.read()
        except urllib2.HTTPError as e:
            return HttpResponse(e.msg, status=e.code, mimetype='text/plain')
        else:
            return HttpResponse(content, status=status_code, mimetype=mimetype)
