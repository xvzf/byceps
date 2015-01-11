# -*- coding: utf-8 -*-

"""
byceps.application
~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from flask import Flask, g
import jinja2
from pathlib import Path

from .blueprints.snippet.init import add_routes_for_snippets
from . import config
from .config import SiteMode
from .database import db
from .mail import mail
from .util import dateformat
from .util.framework import load_config, register_blueprint
from .util.l10n import set_locale


BLUEPRINTS = [
    ('authorization',       '/authorization',       None           ),
    ('authorization_admin', '/admin/authorization', SiteMode.admin ),
    ('board',               '/board',               SiteMode.public),
    #('brand',               None,                   None           ),
    ('core',                '/core',                None           ),
    ('newsletter',          '/newsletter',          None           ),
    ('newsletter_admin',    '/admin/newsletter',    SiteMode.admin ),
    ('orga',                '/orgas',               SiteMode.public),
    ('orga_admin',          '/admin/orgas',         SiteMode.admin ),
    ('orga_presence',       '/admin/presence',      SiteMode.admin ),
    ('party',               None,                   SiteMode.public),
    ('party_admin',         '/admin/parties',       SiteMode.admin ),
    ('seating',             '/seating',             SiteMode.public),
    ('shop',                '/shop',                SiteMode.public),
    ('shop_admin',          '/admin/shop',          SiteMode.admin ),
    ('snippet',             '/snippets',            None           ),
    ('snippet_admin',       '/admin/snippets',      SiteMode.admin ),
    ('terms',               '/terms',               SiteMode.public),
    ('terms_admin',         '/admin/terms',         SiteMode.admin ),
    ('ticket',              '/tickets',             SiteMode.public),
    ('ticket_admin',        '/admin/tickets',       SiteMode.admin ),
    ('tourney',             '/tourney',             SiteMode.public),
    ('user',                '/users',               None           ),
    ('user_admin',          '/admin/users',         SiteMode.admin ),
    ('user_group',          '/user_groups',         SiteMode.public),
]


def create_app(environment_name, *, initialize=True):
    """Create the actual Flask application."""
    app = Flask(__name__)

    load_config(app, environment_name)

    # Throw an exception when an undefined name is referenced in a template.
    app.jinja_env.undefined = jinja2.StrictUndefined

    # Set the locale.
    set_locale(app.config['LOCALE'])  # Fail if not configured.

    # Initialize database.
    db.init_app(app)

    mail.init_app(app)

    config.init_app(app)

    register_blueprints(app)

    dateformat.register_template_filters(app)

    if initialize:
        with app.app_context():
            set_root_path(app)

            if config.get_site_mode().is_public():
                party_id = config.get_current_party_id()

                # Mount snippets.
                add_routes_for_snippets(party_id)

                # Incorporate template overrides for the current party.
                app.template_folder = str(Path('party_template_overrides') \
                                    / party_id)

    return app


def register_blueprints(app):
    """Register the blueprints that are relevant for the current mode."""
    current_mode = config.get_site_mode(app)

    for name, url_prefix, mode in BLUEPRINTS:
        if mode is None or mode == current_mode:
            register_blueprint(app, name, url_prefix)


def set_root_path(app):
    """Set an optioanl URL path to redirect to from the root URL path (`/`).

    Important: Don't specify the target with a leading slash unless you
    really mean the root of host.
    """
    target = app.config.get('ROOT_REDIRECT_TARGET')
    if target:
        app.add_url_rule('/', endpoint='root', redirect_to=target)
