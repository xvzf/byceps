# -*- coding: utf-8 -*-

"""
byceps.services.user_activity.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import namedtuple
from enum import Enum


Activity = namedtuple('Activity', ['occured_at', 'type', 'object'])


ActivityType = Enum('ActivityType', [
    'avatar_update',
    'newsletter_subscription_update',
    'terms_consent',
])