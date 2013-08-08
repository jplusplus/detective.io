#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db.models               import get_app, get_models
from djangular.forms.angular_model  import NgModelFormMixin
from django.forms                   import ModelForm
from django.http                    import Http404
from django.shortcuts               import render_to_response
from django.template                import TemplateDoesNotExist

def home(request):    
    # Render template without any argument
    response = render_to_response('home.dj.html')

    # Add a cookie containing some user information
    if request.user.is_authenticated():
        # Create the cookie
        response.set_cookie("user__is_logged", True)
        response.set_cookie("user__username",  request.user.username)
    else:
        # Deletre existing cookie
        response.delete_cookie("user__is_logged")
        response.delete_cookie("user__username")

    return response


def partial(request, partial_name=None):    
    template_name = 'partials/' + partial_name + '.dj.html';
    try:
        return render_to_response(template_name)
    except TemplateDoesNotExist:
        raise Http404

def partial_contribute(request):
    locales = { 'forms': [] }
    template_name = 'partials/contribute.dj.html';

    app = get_app('detective')
    # For each models into app
    for m in get_models(app):        
        # Create a form using the current model
        class Form(NgModelFormMixin, ModelForm):            
            class Meta:
                model = m      
                #self.fields.keyOrder = 
        form = Form(scope_prefix='individual.fields')        
        # Remove field terminating by +
        form.fields = dict( (k, v) for k, v in form.fields.items() if not k.endswith("+") )
        # Add the form to the forms' list
        locales["forms"].append( form )

    return render_to_response(template_name, locales)   
