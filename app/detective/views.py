#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf                  import settings
from django.contrib.auth          import get_user_model
from django.core.exceptions       import ObjectDoesNotExist
from django.http                  import Http404, HttpResponse
from django.shortcuts             import render_to_response, redirect
from django.template              import TemplateDoesNotExist
from django.views.decorators.gzip import gzip_page
from app.detective.models         import Topic, DetectiveProfileUser
from app.detective.utils          import get_topic_model
import logging
import urllib2
import mimetypes

logger = logging.getLogger(__name__)

APP_TITLE = settings.APP_TITLE

def __get_user(request, **kwargs):
    return get_user_model().objects.get(username=kwargs.get('user'))

def __get_topic(request=None, author=None, **kwargs):
    # fail-proof topic retrieval function
    if not author:
        author = __get_user(request, **kwargs)
    return Topic.objects.get(
        author=author,
        slug=kwargs.get('topic')
    )

def __get_entity(topic_obj, **kwargs):
    # fail-proof entity retrieval function
    entity = None
    Model = get_topic_model(topic_obj, kwargs.get('type'))
    if Model:
        entity = Model.objects.get(pk=kwargs.get('pk'))
    return entity


def default_social_meta(request):
    return {
        "title": "Collaborative network analysis - %s" % APP_TITLE,
        "description": (
            "{app_title} makes it easy to explore networks. Because it "
            "structures your research, you can analyze connections in your "
            "collected data in seconds."
        ).format(app_title=APP_TITLE),
        "url": request.build_absolute_uri()
    }

@gzip_page
def home(request, social_meta_dict=None,**kwargs):
    if social_meta_dict == None:
        social_meta_dict = default_social_meta(request)

    # Render template without any argument
    response = render_to_response('home.dj.html', { 'meta': social_meta_dict, 'debug': settings.DEBUG } )

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

def entity_list(request, **kwargs):
    def __entity_type_name(entity_klass):
        type_name           = None
        verbose_name        = getattr(entity_klass, 'verbose_name', None)
        verbose_name_plural = getattr(entity_klass, 'verbose_name_plural', None)
        if verbose_name_plural:
            type_name = verbose_name_plural
        elif verbose_name:
            type_name = verbose_name + 's'
        else:
            type_name = entity_klass.__name__ + 's'
        return type_name

    def __entity_type_description(entity_klass):
        return getattr(entity_klass, 'help_text', None)

    meta_dict = None
    try:
        user      = __get_user(request, **kwargs)
        topic     = __get_topic(request, user, **kwargs)

        if not topic.public:
            return home(request, None, **kwargs)

        if topic.public and user:
            default_meta = default_social_meta(request)
            entity_klass = get_topic_model(topic, kwargs.get('type'))
            if entity_klass:
                pictures = []
                if topic.background:
                    pictures.append(topic.background)


                list_title = u"{name} of {topic} by {owner}".format(
                    name=__entity_type_name(entity_klass),
                    topic=topic.title,
                    owner=user.username
                )
                meta_title = u"{list_title} - {title}".format(
                    list_title=list_title,
                    title=APP_TITLE
                )
                meta_description = __entity_type_description(entity_klass) or \
                                   topic.description or default_meta['description']
                meta_dict = {
                    'title'       : meta_title,
                    'description' : meta_description,
                    'pictures'    : pictures,
                    'url'         : default_meta['url']
        }
        return home(request, meta_dict, **kwargs)

    except ObjectDoesNotExist as e:
        logger.debug("Tried to access a non-existing model %s" % e)
        return home(request, None, **kwargs)

def entity_details(request, **kwargs):
    def __entity_title(entity):
        title = getattr(entity, '_transform', None) or \
                getattr(entity, 'name'      , None) or \
                getattr(entity, 'value'     , None) or \
                getattr(entity, 'title'     , None) or \
                getattr(entity, 'units'     , None) or \
                getattr(entity, 'label'     , None) or \
                getattr(entity, 'pk'        , None)
        return title

    def __entity_description(entity):
        description = getattr(entity, 'description', None) or \
                      getattr(entity, 'comment'    , None) or \
                      getattr(entity, 'commentary' , None)
        return description

    def __entity_picture(entity): return getattr(entity, 'image', None)

    try:
        user  = __get_user(request, **kwargs)
        topic = __get_topic(request, user, **kwargs)
        if not topic.public:
            return home(request, None, **kwargs)

        meta_pictures = []
        default_meta  = default_social_meta(request)
        entity        = __get_entity(topic, **kwargs)
        entity_title        = __entity_title(entity)
        entity_picture      = __entity_picture(entity)
        entity_description  = __entity_description(entity)
        generic_description = u"{title} is part of the collection {topic} by {owner}".format(
            title=entity_title,
            topic=topic.title,
            owner=user.username
        )

        meta_title = u"{entity_title} - {app_title}".format(
            entity_title=entity_title,
            app_title=APP_TITLE
        )
        meta_description = entity_description or generic_description
        if topic.background:
            meta_pictures.append(topic.background.url)

        if entity_picture:
            meta_pictures.append(entity_picture)

        meta_dict = {
            'title'      : meta_title,
            'description': meta_description,
            'pictures'   : meta_pictures,
            'url'        : default_meta['url']
        }
        return home(request, meta_dict, **kwargs)

    except ObjectDoesNotExist as e:
        logger.debug("Tried to access a non-existing model %s" % e)
        return home(request, None, **kwargs)

def topic(request, **kwargs):
    try:
        user  = __get_user(request, **kwargs)
        topic = __get_topic(request, user, **kwargs)
        if not topic.public:
            return home(request, None, **kwargs)

        default_meta  = default_social_meta(request)
        generic_description = (
            u"Part of collection {topic_title} by {owner} on {app_title}"
        ).format(
            topic_title=topic.title,
            owner=user.username,
            app_title=APP_TITLE
        )

        meta_description = getattr(topic, 'about', None) or generic_description
        meta_pictures    = []
        if topic.background:
            meta_pictures.append(topic.background.url)

        meta_title = u"{topic_title} - {app_title}".format(
            topic_title=topic.title,
            app_title=APP_TITLE
        )

        meta_dict = {
            'title'       : meta_title,
            'description' : meta_description,
            'pictures'    : meta_pictures,
            'url'         : default_meta['url']
        }
        return home(request, meta_dict, **kwargs)
    except ObjectDoesNotExist as e:
        logger.debug("Tried to access a non-existing model %s" % e)
        return home(request, None, **kwargs)

def profile(request, **kwargs):
    try:
        user          = __get_user(request, **kwargs)
        profile       = DetectiveProfileUser.objects.get(user=user)
        default_meta  = default_social_meta(request)
        meta_title = "{user} - {app_title}".format(
            user=user.username, app_title=APP_TITLE
        )
        meta_description = "{user}'s profile on {app_title}".format(
            user=user.username, app_title=APP_TITLE
        )

        meta_dict = {
            'title': meta_title,
            'description': meta_description,
            'pictures': [ profile.avatar ],
            'url': default_meta['url']
        }
        return home(request, meta_dict, **kwargs)
    except ObjectDoesNotExist as e:
        logger.debug("Tried to access a non-existing model %s" % e)
        return home(request, None, **kwargs)

@gzip_page
def partial(request, partial_name=None):
    template_name = 'partials/' + partial_name + '.dj.html'
    try:
        return render_to_response(template_name)
    except TemplateDoesNotExist:
        raise Http404

@gzip_page
def partial_explore(request, topic=None):
    template_name = 'partials/topic.explore.' + topic + '.dj.html'
    try:
        return render_to_response(template_name)
    except TemplateDoesNotExist:
        return partial(request, partial_name='topic.explore.common')

def not_found(request):
    return redirect("/404/")

def proxy(request, name=None):
    def build_header_dict_from_request(request):
        trad = {
            'HTTP_ACCEPT_ENCODING'  : 'Accept-Encoding',
            'HTTP_ACCEPT_LANGUAGE'  : 'Accept-Language'
        }
        new_headers = {}
        for origin, trad in trad.items():
            new_headers[ trad] = request.META[origin]
        return new_headers

    if settings.STATIC_URL[0] == '/':
        return redirect('%s%s' % (settings.STATIC_URL, name));
    else:
        url = '%s%s' % (settings.STATIC_URL, name)
        try :
            request = urllib2.Request(url, None, build_header_dict_from_request(request))
            proxied = urllib2.urlopen(request)
            status_code = proxied.code
            mimetype = proxied.headers.typeheader or mimetypes.guess_type(url)
            content_type     = proxied.headers.dict['content-type']
            content_encoding = proxied.headers.dict.get('content-encoding')
            content  = proxied.read()
        except urllib2.HTTPError as e:
            return HttpResponse(e.msg, status=e.code, mimetype='text/plain')
        else:
            response = HttpResponse(content, content_type=content_type, status=status_code, mimetype=mimetype)
            response['Content-Encoding'] = content_encoding
            return response
