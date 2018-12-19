from django.conf import settings
from django.utils.text import slugify
from django.urls import resolve
from django.http import Http404, HttpResponseRedirect
import re

def SubDomainAuthMiddleware(get_response):  # noqa: N802, C901

    def should_redirect(http_host, sub_domain):
        """
        Return True if the client is acessing a subdomain. Return False
        otherwise. The subdomain must run with https in order to this
        method works properly.
        """
        #removes https scheme from sub_domain
        sub_domain_without_scheme = sub_domain[8:]
        #removes the subdomain routes, as /<board>/conversations
        sub_domain_without_routes = sub_domain_without_scheme[
            :sub_domain_without_scheme.find('/')
        ]
        return http_host == sub_domain_without_routes

    def middleware(request):
        """
        This middleware is responsible to redirect the user to the domain
        configured on platforms as facebook and google for social login.
        If the user is accessing from https://example.ejplatform.org and try to login,
        this middleware will redirect the user to https://ejplatform.org.
        The script `subDomainRedirect.js` is responsible
        to redirect the user back to the subdomain, after him properly login.

        If the user is accessing from the domain, this middleware does not
        trigger a redirect.
        """
        response = get_response(request)
        if(request.path == '/login/' and request.META.get('HTTP_HOST')):
            sub_domain = request.GET.get('next')
            if (sub_domain):
                domain_with_social_app = sub_domain[sub_domain.find('.')+1:]
                domain_with_social_app = domain_with_social_app[:domain_with_social_app.find('/')]
                is_a_sub_domain = should_redirect(request.META['HTTP_HOST'],
                                                  sub_domain)
                if (is_a_sub_domain):
                    from django.http import HttpResponseRedirect
                    response_url = 'https://%s/login/?next=%s' % (domain_with_social_app,
                                                                  sub_domain)
                    return HttpResponseRedirect(response_url)
        return response

    return middleware
