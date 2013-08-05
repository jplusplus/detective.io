#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db.models               import get_app, get_models
from djangular.forms.angular_model  import NgModelFormMixin
from django.forms                   import ModelForm
from django.http                    import Http404
from django.shortcuts               import render_to_response
from django.template                import RequestContext, TemplateDoesNotExist



@login_required
def home(request):
    locales = {}
    return render_to_response('home.dj.html', locales, context_instance=RequestContext(request))

def partial(request, partial_name=None):    
    locales = {}
    template_name = 'partials/' + partial_name + '.dj.html';
    try:
        return render_to_response(template_name, locales, context_instance=RequestContext(request))    
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
        # Add the form to the forms' list
        locales["forms"].append( Form(scope_prefix='individual.fields') )

    return render_to_response(template_name, locales, context_instance=RequestContext(request))   
