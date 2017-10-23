from sqlalchemy import Table, Column, String, Integer, ForeignKey, DateTime, orm, inspect
from tubelocal import Base, jsonify


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<Artist(name='%s')>" % (self.name)

    def toDict(self, to_json=False):
        artist_dict = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        return jsonify(artist_dict) if to_json else artist_dict


# many to many Collection<->Video
collection_videos = Table(
    'collection_videos', Base.metadata,
    Column('collection_id', ForeignKey('collections.id'), primary_key=True),
    Column('video_id', ForeignKey('videos.id'), primary_key=True)
)


class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist_id = Column(Integer, ForeignKey('artists.id'))
    duration = Column(Integer)
    canonical_url = Column(String)
    poster_filename = Column(String)
    video_filename = Column(String)
    created_at = Column(DateTime)

    collections = orm.relationship(
        'Collection',
        secondary=collection_videos,
        back_populates='videos'
    )
    artist = orm.relationship('Artist', lazy='joined')

    def __repr__(self):
        return "<Video(title='%s')>" % (self.title)

    def toDict(self, to_json=False):
        video_model = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        if getattr(self, 'artist'):
            video_model['artist'] = getattr(self, 'artist').toDict()

        return jsonify(video_model) if to_json else video_model


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    videos = orm.relationship(
        'Video',
        secondary=collection_videos,
        back_populates='collections'
    )
