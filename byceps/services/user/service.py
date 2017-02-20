# -*- coding: utf-8 -*-

"""
byceps.services.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from flask import current_app, url_for

from ...database import db

from ..authentication.password import service as password_service
from ..authorization import service as authorization_service
from ..email import service as email_service
from ..newsletter import service as newsletter_service
from ..orga_team.models import OrgaTeam, Membership as OrgaTeamMembership
from ..terms import service as terms_service
from ..user_avatar.models import Avatar, AvatarSelection
from ..verification_token import service as verification_token_service

from .models.detail import UserDetail
from .models.user import AnonymousUser, User, UserTuple


def count_users():
    """Return the number of users."""
    return User.query \
        .count()


def count_users_created_since(delta):
    """Return the number of user accounts created since `delta` ago."""
    filter_starts_at = datetime.now() - delta

    return User.query \
        .filter(User.created_at >= filter_starts_at) \
        .count()


def count_enabled_users():
    """Return the number of enabled user accounts."""
    return User.query \
        .filter_by(enabled=True) \
        .count()


def count_disabled_users():
    """Return the number of disabled user accounts."""
    return User.query \
        .filter_by(enabled=False) \
        .count()


def find_user(user_id, *, with_orga_teams=False):
    """Return the user with that ID, or `None` if not found."""
    query = User.query

    if with_orga_teams:
        query = query.options(
            db.joinedload('orga_team_memberships').joinedload('orga_team').joinedload('party')
        )

    return query.get(user_id)


def find_users(user_ids, *, party_id=None):
    """Return the users and their current avatars' URLs with those IDs."""
    rows = db.session \
        .query(User.id, User.screen_name, User.deleted, Avatar) \
        .outerjoin(AvatarSelection) \
        .outerjoin(Avatar) \
        .filter(User.id.in_(frozenset(user_ids))) \
        .all()

    if party_id is not None:
        orga_team_members = db.session \
            .query(OrgaTeamMembership.user_id) \
            .join(OrgaTeam) \
            .filter(OrgaTeam.party_id == party_id) \
            .filter(OrgaTeamMembership.user_id.in_(frozenset(user_ids))) \
            .group_by(OrgaTeamMembership.user_id) \
            .having(db.func.count(OrgaTeamMembership.user_id) > 0) \
            .all()
    else:
        orga_team_members = frozenset()

    def to_tuples():
        for user_id, screen_name, is_deleted, avatar in rows:
            avatar_url = avatar.url if avatar else None
            is_orga = user_id in orga_team_members

            yield UserTuple(
                user_id,
                screen_name,
                is_deleted,
                avatar_url,
                is_orga
            )

    return set(to_tuples())


def find_user_by_screen_name(screen_name):
    """Return the user with that screen name, or `None` if not found."""
    return User.query \
        .filter_by(screen_name=screen_name) \
        .one_or_none()


def get_anonymous_user():
    """Return the anonymous user."""
    return AnonymousUser()


def is_screen_name_already_assigned(screen_name):
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(User.screen_name, screen_name)


def is_email_address_already_assigned(email_address):
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(User.email_address, email_address)


def _do_users_matching_filter_exist(model_attribute, search_value):
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    user_count = User.query \
        .filter(db.func.lower(model_attribute) == search_value.lower()) \
        .count()
    return user_count > 0


class UserCreationFailed(Exception):
    pass


def create_user(screen_name, email_address, password, first_names, last_name,
                brand_id, subscribe_to_newsletter):
    """Create a user account and related records."""
    # user with details
    user = build_user(screen_name, email_address)
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    db.session.add(user)

    # roles
    board_user_role = authorization_service.find_role('board_user')
    authorization_service.assign_role_to_user(board_user_role, user)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error('User creation failed: %s', e)
        db.session.rollback()
        raise UserCreationFailed()

    # password
    password_service.create_password_hash(user.id, password)

    # consent to terms of service (required)
    terms_version = terms_service.get_current_version(brand_id)
    terms_consent = terms_service.build_consent_on_account_creation(user.id,
                                                                    terms_version.id)
    db.session.add(terms_consent)
    db.session.commit()

    # newsletter subscription (optional)
    _create_newsletter_subscription(user.id, brand_id, subscribe_to_newsletter)

    # verification_token for email address confirmation
    verification_token = verification_token_service \
        .build_for_email_address_confirmation(user.id)
    db.session.add(verification_token)
    db.session.commit()

    send_email_address_confirmation_email(user, verification_token)

    return user


def build_user(screen_name, email_address):
    normalized_screen_name = _normalize_screen_name(screen_name)
    normalized_email_address = _normalize_email_address(email_address)

    user = User(normalized_screen_name, normalized_email_address)

    detail = UserDetail(user=user)

    return user


def _normalize_screen_name(screen_name):
    """Normalize the screen name, or raise an exception if invalid."""
    normalized = screen_name.strip()
    if not normalized or (' ' in normalized) or ('@' in normalized):
        raise ValueError('Invalid screen name: \'{}\''.format(screen_name))
    return normalized


def _normalize_email_address(email_address):
    """Normalize the e-mail address, or raise an exception if invalid."""
    normalized = email_address.strip()
    if not normalized or (' ' in normalized) or ('@' not in normalized):
        raise ValueError('Invalid email address: \'{}\''.format(email_address))
    return normalized


def _create_newsletter_subscription(user_id, brand_id, subscribe_to_newsletter):
    if subscribe_to_newsletter:
        newsletter_service.subscribe(user_id, brand_id)
    else:
        newsletter_service.unsubscribe(user_id, brand_id)


def send_email_address_confirmation_email(user, verification_token):
    confirmation_url = url_for('.confirm_email_address',
                               token=verification_token.token,
                               _external=True)

    subject = '{0.screen_name}, bitte bestätige deine E-Mail-Adresse'.format(user)
    body = (
        'Hallo {0.screen_name},\n\n'
        'bitte bestätige deine E-Mail-Adresse indem du diese URL abrufst: {1}'
    ).format(user, confirmation_url)
    recipients = [user.email_address]

    email_service.send_email(subject=subject, body=body, recipients=recipients)


def confirm_email_address(verification_token):
    """Confirm the email address of the user assigned with that
    verification token.
    """
    user = verification_token.user

    user.enabled = True
    db.session.delete(verification_token)
    db.session.commit()


def update_user_details(user, first_names, last_name, date_of_birth, country,
                        zip_code, city, street, phone_number):
    """Update the user's details."""
    user.detail.first_names = first_names
    user.detail.last_name = last_name
    user.detail.date_of_birth = date_of_birth
    user.detail.country = country
    user.detail.zip_code = zip_code
    user.detail.city = city
    user.detail.street = street
    user.detail.phone_number = phone_number

    db.session.commit()
