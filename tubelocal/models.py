from sqlalchemy import Table, Column, String, Integer, ForeignKey, DateTime, orm
from tubelocal import Base


class Artist(Base):
    __tablename__ = 'artists'
    id = Column(Integer, primary_key=True)
    name = Column(String)


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
    poster_url = Column(String)
    video_url = Column(String)
    created_at = Column(DateTime)

    collections = orm.relationship(
        'Collection',
        secondary=collection_videos,
        back_populates='videos'
    )


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    videos = orm.relationship(
        'Video',
        secondary=collection_videos,
        back_populates='collections'
    )
