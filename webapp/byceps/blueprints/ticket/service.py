# -*- coding: utf-8 -*-

"""
byceps.blueprints.ticket.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ..party.models import Party
from ..seating.models import Category

from .models import Ticket


def find_ticket_for_user(user, party):
    """Return the ticket used by the user for the party, or `None` if not
    found.
    """
    return Ticket.query \
        .filter(Ticket.used_by == user) \
        .for_party(party) \
        .first()


def get_attended_parties(user):
    """Return the parties the user has attended."""
    return Party.query \
        .join(Category).join(Ticket).filter(Ticket.used_by == user) \
        .all()
