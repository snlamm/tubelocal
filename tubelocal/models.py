from sqlalchemy import Table, Column, String, Integer, ForeignKey, DateTime, orm, inspect
from tubelocal import Base, jsonify, abort


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    videos = orm.relationship('Video')

    def __repr__(self):
        return "<Artist(name='%s')>" % (self.name)

    def toDict(self, to_json=False, use_eager=True):
        artist_dict = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        if use_eager and getattr(self, 'videos'):
            artist_dict['videos'] = [c.toDict(use_eager=False) for c in getattr(self, 'videos')]

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
        back_populates='videos',
        lazy='joined'
    )
    artist = orm.relationship('Artist', lazy='joined')

    def __repr__(self):
        return "<Video(title='%s')>" % (self.title)

    def toDict(self, to_json=False, use_eager=True, get_collections=True):
        video_model = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        if use_eager and getattr(self, 'artist'):
            video_model['artist'] = getattr(self, 'artist').toDict(use_eager=False)

        if use_eager and getattr(self, 'collections') and get_collections:
            video_model['collections'] = [c.toDict(use_eager=False) for c in getattr(self, 'collections')]

        return jsonify(video_model) if to_json else video_model


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    videos = orm.relationship(
        'Video',
        secondary=collection_videos,
        back_populates='collections',
        lazy='subquery'
    )

    def __repr__(self):
        return "<Collection(name='%s')>" % (self.name)

    def toDict(self, to_json=False, use_eager=True):
        collection_dict = {c: getattr(self, c) for c in ['id', 'name']}

        if use_eager and getattr(self, 'videos'):
            collection_dict['videos'] = [video.toDict(get_collections=False) for video in getattr(self, 'videos')]

        return jsonify(collection_dict) if to_json else collection_dict


def find_or_404(modelClass, model_id):
    model = modelClass.query.get(model_id)
    return model if model else abort(404)
