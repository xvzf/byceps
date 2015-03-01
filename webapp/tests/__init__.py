# -*- coding: utf-8 -*-

from contextlib import contextmanager
from unittest import TestCase

from byceps.application import create_app
from byceps.database import db

from testfixtures.brand import create_brand
from testfixtures.party import create_party


class AbstractAppTestCase(TestCase):

    def setUp(self, env='test'):
        self.app = create_app(env, initialize=False)

        self.db = db
        db.app = self.app

        db.reflect()
        db.drop_all()
        db.create_all()

        self.create_brand_and_party()

    def create_brand_and_party(self):
        self.brand = create_brand()
        db.session.add(self.brand)

        self.party = create_party(brand=self.brand)
        db.session.add(self.party)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @contextmanager
    def client(self, *, user=None):
        """Provide an HTTP client.

        If a user is given, the client authenticates with the user's
        credentials.
        """
        client = self.app.test_client()

        if user is not None:
            add_user_credentials_to_session(client, user)

        yield client


def add_user_credentials_to_session(client, user):
    with client.session_transaction() as session:
        session['user_id'] = str(user.id)
        session['user_auth_token'] = str(user.auth_token)
