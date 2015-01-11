# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from ...util.l10n import LocalizedForm


class PostingCreateForm(LocalizedForm):
    body = TextAreaField('Text', validators=[DataRequired()])


class PostingUpdateForm(PostingCreateForm):
    pass


class TopicCreateForm(PostingCreateForm):
    title = StringField('Titel', validators=[DataRequired()])


class TopicUpdateForm(TopicCreateForm):
    pass
