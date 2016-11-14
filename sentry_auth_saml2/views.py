from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config
from sentry.auth import AuthView

from .forms import ConfigureForm


class SetupView(AuthView):
    def dispatch(self, request, helper):
        if 'metadata_url' in request.POST:
            form = ConfigureForm(request.POST)
            if form.is_valid():
                data = form.clean()
                helper.bind_state('metadata_url', data['metadata_url'])
                return helper.next_step()
        else:
            form = ConfigureForm(initial=request.POST)
        return render(request, 'sentry_auth_saml2/setup.html', {'form': form})


class RequestView(AuthView):
    def __init__(self, metadata_url=None):
        self.metadata_url = metadata_url
        super(RequestView, self).__init__()

    def dispatch(self, request, helper):
        if self.metadata_url is None:
            metadata_url = helper.fetch_state('metadata_url')
        else:
            metadata_url = self.metadata_url
        org = self.get_active_organization(request)
        settings = {
            'entityid': request.build_absolute_uri(
                '/organizations/%s/' % org.slug
            ),
            'metadata': {
                'remote': [{
                    'url': metadata_url,
                }],
            },
            'service': {
                'sp': {
                    'endpoints': {
                        'assertion_consumer_service': [(
                            request.build_absolute_uri(
                                reverse('sentry-auth-sso')
                            ),
                            BINDING_HTTP_POST
                        )],
                    },
                    'allow_unsolicited': False,
                    'authn_requests_signed': False,
                    'logout_requests_signed': True,
                    'want_assertions_signed': False,
                    'want_response_signed': True,
                },
            },
        }
        config = Config()
        config.load(settings)
        client = Saml2Client(config)
        request_id, headers = client.prepare_for_authenticate()
        helper.bind_state('request_id', request_id)
        for key, value in headers['headers']:
            if key is 'Location':
                # helper.incr_step()
                helper.request.session['auth']['idx'] += 1
                helper.request.session.modified = True
                return self.redirect(value)
        # TODO: I think this should never happen, but what to do if we hit this?


class ResponseView(AuthView):
    def __init__(self, metadata_url=None):
        self.metadata_url = metadata_url
        super(ResponseView, self).__init__()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, helper):
        if self.metadata_url is None:
            metadata_url = helper.fetch_state('metadata_url')
        else:
            metadata_url = self.metadata_url
        request_id = helper.fetch_state('request_id')
        settings = {
            'entityid': request.build_absolute_uri(
                '/organizations/%s/' % helper.organization.slug
            ),
            'metadata': {
                'remote': [{
                    'url': metadata_url,
                }],
            },
            'service': {
                'sp': {
                    'endpoints': {
                        'assertion_consumer_service': [(
                            request.build_absolute_uri(
                                reverse('sentry-auth-sso')
                            ),
                            BINDING_HTTP_POST
                        )],
                    },
                    'allow_unsolicited': False,
                    'authn_requests_signed': False,
                    'logout_requests_signed': True,
                    'want_assertions_signed': False,
                    'want_response_signed': True,
                },
            },
        }
        config = Config()
        config.load(settings)
        client = Saml2Client(config)
        response = client.parse_authn_request_response(
            request.POST['SAMLResponse'],
            BINDING_HTTP_POST,
            outstanding={
                request_id: True
            }
        )
        extra = {
            key.lower(): value
            for key, value in
            response.get_identity().items()
            }
        user_info = response.get_subject()
        email = user_info.text
        username, domain = email.rsplit('@', 1)

        if not email:
            return helper.error('no email')

        helper.bind_state('email', email)
        helper.bind_state('name', extra.get('name', username))

        return helper.next_step()
