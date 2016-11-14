from __future__ import absolute_import, print_function

from sentry.auth.provider import Provider

from .views import SetupView, RequestView, ResponseView


class SAML2Provider(Provider):
    name = 'SAML2'

    def __init__(self, metadata_url=None, **config):
        self.metadata_url = metadata_url
        super(SAML2Provider, self).__init__(**config)

    def build_config(self, state):
        return {
            'metadata_url': state['metadata_url'],
        }

    def get_setup_pipeline(self):
        return [
            SetupView(),
            RequestView(metadata_url=self.metadata_url),
            ResponseView(metadata_url=self.metadata_url),
        ]

    def get_auth_pipeline(self):
        return [
            RequestView(metadata_url=self.metadata_url),
            ResponseView(metadata_url=self.metadata_url),
        ]

    def refresh_identity(self, auth_identity):
        pass

    def build_identity(self, state):
        return {
            'id': state['email'],
            'email': state['email'],
            'name': state['name'],
        }
