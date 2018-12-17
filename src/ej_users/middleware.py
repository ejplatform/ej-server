from django.conf import settings
from django.utils.text import slugify
from django.urls import resolve
from django.http import Http404, HttpResponsePermanentRedirect
import re

def CustomDomainAuthMiddleware(get_response):  # noqa: N802, C901

    def should_redirect(http_host, sub_domain):
        """
        Return True if the client is acessing a subdomain. Return False
        otherwise.
        """
        #removes https scheme from sub_domain
        sub_domain_without_scheme = sub_domain[8:]
        #removes the subdomain routes, as /<board>/conversations
        sub_domain_without_routes = sub_domain_without_scheme[
            :sub_domain_without_scheme.find('/')
        ]
        return http_host == sub_domain_without_routes

    def middleware(request):
        response = get_response(request)
        if(request.path == '/login/'):
            sub_domain = request.GET.get('next')
            domain_with_social_app = sub_domain[sub_domain.find('.')+1:]
            domain_with_social_app = domain_with_social_app[:domain_with_social_app.find('/')]
            is_a_sub_domain = should_redirect(request.META['HTTP_HOST'],
                                              sub_domain)
            if (is_a_sub_domain):
                from django.http import HttpResponsePermanentRedirect
                response_url = 'https://%s/login/?next=%s' % (domain_with_social_app,
                                                              sub_domain)
                return HttpResponsePermanentRedirect(response_url)
            else:
                return response
        return response

    return middleware
