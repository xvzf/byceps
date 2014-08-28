# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from datetime import datetime

from flask import g

from ...database import BaseQuery, db, generate_uuid
from ...util.instances import ReprBuilder

from ..brand.models import Brand
from ..user.models import User


class CategoryQuery(BaseQuery):

    def for_current_brand(self):
        return self.filter_by(brand=g.party.brand)


class Category(db.Model):
    """A category for topics."""
    __tablename__ = 'board_categories'
    __table_args__ = (
        db.UniqueConstraint('brand_id', 'title'),
        db.UniqueConstraint('brand_id', 'position'),
    )
    query_class = CategoryQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'))
    brand = db.relationship(Brand)
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Unicode(40), nullable=False)
    description = db.Column(db.Unicode(80))
    topic_count = db.Column(db.Integer, default=0)
    posting_count = db.Column(db.Integer, default=0)
    last_posting_updated_at = db.Column(db.DateTime)
    last_posting_author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_posting_author = db.relationship(User)

    def aggregate(self):
        """Update the count and latest fields."""
        topic_count = Topic.query.filter_by(category=self).count()
        posting_query = Posting.query.join(Topic).filter_by(category=self)
        posting_count = posting_query.count()
        last_posting = posting_query.order_by(Posting.created_at.desc()).first()

        self.topic_count = topic_count
        self.posting_count = posting_count
        self.last_posting_updated_at = last_posting.created_at if last_posting else None
        self.last_posting_author = last_posting.author if last_posting else None

        db.session.commit()

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('brand') \
            .add_with_lookup('title') \
            .build()


class Topic(db.Model):
    """A topic."""
    __tablename__ = 'board_topics'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    category_id = db.Column(db.Uuid, db.ForeignKey('board_categories.id'))
    category = db.relationship(Category, backref='topics')
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    author = db.relationship(User, foreign_keys=[author_id])
    title = db.Column(db.Unicode(80))
    posting_count = db.Column(db.Integer, default=0)
    last_updated_at = db.Column(db.DateTime, default=datetime.now())
    last_author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_author = db.relationship(User, foreign_keys=[last_author_id])
    hidden = db.Column(db.Boolean, default=False)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])
    locked = db.Column(db.Boolean, default=False)
    locked_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    locked_by = db.relationship(User, foreign_keys=[locked_by_id])
    pinned = db.Column(db.Boolean, default=False)
    pinned_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    pinned_by = db.relationship(User, foreign_keys=[pinned_by_id])

    @classmethod
    def create(cls, category, author, title, body):
        topic = Topic(category=category, author=author, title=title)
        posting = Posting(topic, author, body)

        db.session.add(topic)
        db.session.add(posting)

        return topic

    @property
    def new(self):
        return True # TODO

    @property
    def reply_count(self):
        return self.posting_count - 1

    def aggregate(self):
        """Update the count and latest fields.""" # TODO
        posting_count = Posting.query.filter_by(topic=self).count()
        last_posting = Posting.query.filter_by(topic=self).order_by(Posting.created_at.desc()).first()

        self.posting_count = posting_count
        if last_posting:
            self.last_updated_at = last_posting.created_at
            self.last_author = last_posting.author

        db.session.commit()

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('category', self.category.title) \
            .add('author', self.author.screen_name) \
            .add_with_lookup('title')

        if self.hidden:
            builder.add_custom('hidden by {}'.format(self.hidden_by.screen_name))

        if self.locked:
            builder.add_custom('locked by {}'.format(self.locked_by.screen_name))

        if self.pinned:
            builder.add_custom('pinned by {}'.format(self.pinned_by.screen_name))

        return builder.build()


class Posting(db.Model):
    """A posting."""
    __tablename__ = 'board_postings'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'))
    topic = db.relationship(Topic, backref='postings')
    created_at = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    author = db.relationship(User, foreign_keys=[author_id])
    body = db.Column(db.UnicodeText)
    last_edited_at = db.Column(db.DateTime, default=datetime.now())
    last_editor_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    last_editor = db.relationship(User, foreign_keys=[last_editor_id])
    edit_count = db.Column(db.Integer, default=0)
    hidden = db.Column(db.Boolean, default=False)
    hidden_by_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    hidden_by = db.relationship(User, foreign_keys=[hidden_by_id])

    def __init__(self, topic, author, body):
        self.topic = topic
        self.author = author
        self.body = body

    def __repr__(self):
        builder = ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('topic', self.topic.title) \
            .add('author', self.author.screen_name)

        if self.hidden:
            builder.add_custom('hidden by {}'.format(self.hidden_by.screen_name))

        return builder.build()
