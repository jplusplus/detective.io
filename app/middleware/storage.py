#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project: IDF-Quiz
# -----------------------------------------------------------------------------
# Author: Pierre Bellon                               <bellon.pierre@gmail.com>
# -----------------------------------------------------------------------------
# License: GNU General Public License
# -----------------------------------------------------------------------------
# Creation time:      2014-07-29 11:11:42
# Last Modified time: 2014-07-29 18:50:16
# -----------------------------------------------------------------------------
# This file is part of IDF-Quiz
# 
#   IDF-Quiz is a narrative app promoting culture and tourism in Ile-De-France.
#   Copyright (C) 2014 Journalism++
#   
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
from app.detective.models import Topic
import re

class StoreTopicList(object):
    def process_request(self, request):
        request.topic_list = Topic.objects.all()
        return None

class StoreTopic(object):
    def process_request(self, request):
        regex = re.compile(r'api/([a-zA-Z0-9_\-]+)/')
        urlparts = regex.findall(request.path)
        if urlparts:
            try:
                request.current_topic = Topic.objects.get(slug=urlparts[0])
            except Topic.DoesNotExist:
                pass
        return None