#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch
import webapp2

CACHE_EXPIRATION = 60*60*24 # 1 day


class MainHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('url')
        if not url.startswith('http://'):
            url = 'http://%s' %url 
        
        content = memcache.get(url)
        headers = memcache.get('%s:headers' % url)
        status = memcache.get('%s:status' % url)
        if content and headers and status:
            logging.info('cache hit')
            self.generate_response(content, headers, status)
        else:
            logging.info('cache miss')
            result = urlfetch.fetch(url, deadline=60)
            if result.status_code != 200:
                result.content = 'Cannot fetch %s' % url
            
            self.generate_response(result.content, result.headers, result.status_code)
            
            memcache.set(url, result.content, CACHE_EXPIRATION)
            memcache.set('%s:headers' % url, result.headers, CACHE_EXPIRATION)
            memcache.set('%s:status' % url, result.status_code, CACHE_EXPIRATION)


    def generate_response(self, content, headers, status):
        self.response.write(content)
        for key, value in headers.items():
            self.response.headers.add_header(key, value)
        self.response.set_status(status)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=False)
