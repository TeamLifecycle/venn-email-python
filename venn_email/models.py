from abc import ABCMeta, abstractmethod
import os
import sys

import mandrill
import requests
import sendgrid


class AbstractMailProvider(object):
    """A common provider interface for configuration and sending emails."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def config(self, api_keys):
        """Setup the email client."""
        pass

    @abstractmethod
    def send(self, from_, to, subject, body):
        """Send an email."""
        pass


class SendGridEmailProvider(AbstractMailProvider):
    """Send email via SendGrid."""

    name = 'sendgrid'

    def __init__(self):
        pass
        
    def config(self, api_keys):
        super(SendGridEmailProvider, self).config(api_keys)
        self.client = sendgrid.SendGridClient(api_keys['api_user'], api_keys['api_key'])

    def send(self, from_, to, subject, body):
        super(SendGridEmailProvider, self).send(from_, to, subject, body)
        message = sendgrid.Mail(to=to, subject=subject, text=body, from_email=from_)
        status, msg = self.client.send(message)
        return status == 200


class MandrillEmailProvider(AbstractMailProvider):
    """Send email via Mandrill."""

    name = 'mandrill'

    def __init__(self):
        pass

    def config(self, api_keys):
        super(MandrillEmailProvider, self).config(api_keys)
        self.client = mandrill.Mandrill(api_keys['api_key'])

    def send(self, from_, to, subject, body):
        super(MandrillEmailProvider, self).send(from_, to, subject, body)
        message = {
            'from_email': from_,
            'subject': subject,
            'text': body,
            'to': [
                {
                    'email': to,
                    'type': 'to',
                }
            ],
        }
        result = self.client.messages.send(message=message)
        return result[0]['status'] == 'sent'


class VennEmail(object):
    def __init__(self, api_key=None):
        try:
            venn_api_key = api_key or os.environ['VENN_EMAIL_API_KEY']
        except KeyError:
            sys.exit('Don\'t forget to set the VENN_EMAIL_API_KEY environment variable.')
        self.headers = {'venn-api-key': venn_api_key}

        self._retrieve_api_keys()
        self._retrieve_priorities()
        self._config_email_providers()

    def _retrieve_api_keys(self):
        url = 'https://api.getvenn.io/v1/keys/'
        params = {'type': 'email'}
        r = requests.get(url, headers=self.headers, params=params)
        self.keys = r.json() if r.status_code == requests.codes.ok else []

    def _retrieve_priorities(self):
        url = 'https://api.getvenn.io/v1/priority/'
        params = {'type': 'email'}
        r = requests.get(url, headers=self.headers, params=params)
        self.priorities = r.json() if r.status_code == requests.codes.ok else []

    def _config_email_providers(self):
        provider_classes = []

        # TODO: make this not complex
        for i in self.priorities:
            if i == 'mandrill':
                provider_classes.append(MandrillEmailProvider)
            elif i == 'sendgrid':
                provider_classes.append(SendGridEmailProvider)

        self.providers = []
        for p in provider_classes:
            provider = p()
            provider.config(api_keys=self.keys[p.name])
            self.providers.append(provider)

    def send(self, from_, to, subject, body):
        success = False
        sent_with = None

        for p in self.providers:
            success = p.send(from_=from_, to=to, subject=subject, body=body)
            if success:
                sent_with = p.name
                break

        return success, sent_with
