from __future__ import absolute_import

from sentry.auth import register

from .provider import SAML2Provider

register('saml2', SAML2Provider)
