# -*- coding: utf-8 -*-

"""
byceps.blueprints.board_admin.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from wtforms import IntegerField, StringField
from wtforms.validators import InputRequired, Length

from ...util.l10n import LocalizedForm


class CategoryCreateForm(LocalizedForm):
    position = IntegerField('Position', [InputRequired()])
    slug = StringField('Slug', [InputRequired(), Length(max=40)])
    title = StringField('Titel', [InputRequired(), Length(max=40)])
    description = StringField('Text', [InputRequired(), Length(max=80)])


class CategoryUpdateForm(CategoryCreateForm):
    pass