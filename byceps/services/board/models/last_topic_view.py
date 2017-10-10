"""
byceps.services.board.models.last_topic_view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db
from ....typing import UserID
from ....util.instances import ReprBuilder

from .topic import Topic, TopicID


class LastTopicView(db.Model):
    """The last time a user looked into specific topic."""
    __tablename__ = 'board_topics_lastviews'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Uuid, db.ForeignKey('board_topics.id'), primary_key=True)
    topic = db.relationship(Topic)
    occured_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id: UserID, topic_id: TopicID) -> None:
        self.user_id = user_id
        self.topic_id = topic_id

    @classmethod
    def find(cls, user_id: UserID, topic_id: TopicID
            ) -> Optional['LastTopicView']:
        return cls.query \
            .filter_by(user_id=user_id, topic_id=topic_id) \
            .first()

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user_id') \
            .add('topic', self.topic.title) \
            .add_with_lookup('occured_at') \
            .build()