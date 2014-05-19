#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http      import Http404
from django.shortcuts import render_to_response, redirect
from django.template  import TemplateDoesNotExist


def home(request):
    # Render template without any argument
    response = render_to_response('home.dj.html')

    # Add a cookie containing some user information
    if request.user.is_authenticated():
        permissions = request.user.get_all_permissions()
        # Create the cookie
        response.set_cookie("user__is_logged",   1)
        response.set_cookie("user__is_staff",    1*request.user.is_staff)
        response.set_cookie("user__username",    unicode(request.user.username))
        response.set_cookie("user__permissions", unicode(u' '.join(permissions)))
    else:
        # Deletre existing cookie
        response.delete_cookie("user__is_logged")
        response.delete_cookie("user__is_staff")
        response.delete_cookie("user__username")
        response.delete_cookie("user__permissions")

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