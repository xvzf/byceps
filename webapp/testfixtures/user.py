# -*- coding: utf-8 -*-

from byceps.database import generate_uuid

from byceps.blueprints.user.models import User


def create_user(number, *, enabled=True):
    screen_name = 'User-{:d}'.format(number)
    email_address = 'user{:03d}@example.com'.format(number)

    user = User.create(screen_name, email_address, 'le_password')
    user.id = generate_uuid()
    user.enabled = enabled
    return user
