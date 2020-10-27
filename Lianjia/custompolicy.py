from scrapy.utils.httpobj import urlparse_cached

import logging


class CustomPolicy(object):

    def __init__(self, settings):
        self.ignore_schemes = settings.getlist('HTTPCACHE_IGNORE_SCHEMES')
        self.ignore_http_codes = [int(x) for x in settings.getlist('HTTPCACHE_IGNORE_HTTP_CODES')]

    def should_cache_request(self, request):
        return urlparse_cached(request).scheme not in self.ignore_schemes

    def should_cache_response(self, response, request):
        return response.status not in self.ignore_http_codes

    def is_cached_response_fresh(self, response, request):
        if "refresh_cache" in request.meta:
            if request.meta['proxy'] is not None:
                logging.warning("refresh cache works in is_response_fresh" + request.url + request.meta['proxy'])
            else:
                logging.warning("refresh cache works in is_response_fresh" + request.url + 'None')
            return False
        return True

    def is_cached_response_valid(self, cachedresponse, response, request):
        if "refresh_cache" in request.meta:
            if request.meta['proxy'] is not None:
                logging.warning("refresh cache works in is_response_valid" + request.url + request.meta['proxy'])
            else:
                logging.warning("refresh cache works in is_response_valid" + request.url + 'None')
            return False
        return True
