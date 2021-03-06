import os
import webbrowser
import datetime
from tubelocal import Blueprint, request, jsonify, db_session
from ..models import Video, Artist, Collection, find_or_404
import pafy
import urllib.request

videos = Blueprint('videos', 'videos', url_prefix='/videos')


@videos.route('/', methods=['GET'])
def index():
    models = db_session.query(Video).all()
    return jsonify([model.toDict() for model in models])


@videos.route('/<int:video_id>', methods=['GET'])
def show(video_id):
    return find_or_404(Video, video_id).toDict(to_json=True)


@videos.route('/<int:video_id>/play', methods=['GET'])
def play(video_id):
    video_model = find_or_404(Video, video_id)
    filename = video_model.video_filename
    video_storage_path = video_model.storage_path(videos.root_path, filename)

    webbrowser.open('file://' + video_storage_path)
    return 'success'


@videos.route('/', methods=['POST'])
def create():
    # Grab the youtube data
    try:
        url = request.form['url']
        vidData = pafy.new(url)
    except Exception as err:
        raise AttributeError({'url': 'valid url is required'}, err)

    # format basic video info
    title = vidData.title
    poster_url = vidData.bigthumb
    stream = vidData.getbest(preftype='mp4')

    # format duration
    duration_in_seconds = 0
    duration_breakdown = vidData.duration.split(':')
    duration_in_seconds += (int(duration_breakdown[0]) * 60 * 60)
    duration_in_seconds += (int(duration_breakdown[1]) * 60)
    duration_in_seconds += int(duration_breakdown[2])

    # Find or create video artist
    artist_name = vidData.author
    artist_model = db_session.query(Artist).filter_by(name=artist_name).first()
    is_new_artist = bool(artist_model)

    if not artist_model:
        artist_model = Artist(name=artist_name)

    # Create the video model
    vid_model = Video(
        title=title,
        canonical_url=url,
        artist=artist_model,
        created_at=datetime.datetime.now()
    )
    db_session.add(vid_model)
    db_session.commit()

    # Format video and poster filepaths
    base_filename = '%d-%d' % (vid_model.id, vid_model.created_at.timestamp())
    video_filename = base_filename + '.mp4'
    poster_filename = base_filename + '.jpg'
    video_storage_path = vid_model.storage_path(videos.root_path, video_filename)
    poster_storage_path = vid_model.storage_path(videos.root_path, poster_filename, to_video=False)

    # Attempt to download stream to filepath and update video model with it.
    # On error, delete downloads (and artist) if they were created
    try:
        stream.download(quiet=False, filepath=video_storage_path)
        urllib.request.urlretrieve(poster_url, poster_storage_path)

        vid_model.video_filename = video_filename
        vid_model.poster_filename = poster_filename
        vid_model.duration = duration_in_seconds

        db_session.commit()
    except Exception as err:
        if os.path.isfile(video_storage_path):
            os.remove(video_storage_path)

        if os.path.isfile(poster_storage_path):
            os.remove(poster_storage_path)

        if is_new_artist:
            db_session.delete(artist_model)
            db_session.commit()

        raise err

    # Serialize video/artist created
    return vid_model.toDict(to_json=True)


@videos.route('/<int:video_id>', methods=['PATCH'])
def update(video_id):
    video_model = find_or_404(Video, video_id)

    title = request.form.get('title', None)
    collection_ids_string = request.form.get('collection_ids', None)
    collection_ids = collection_ids_string.split(',') if collection_ids_string else []

    if title:
        video_model.title = title

    collections = None

    # Assign multiple collections
    if collection_ids:
        collections = Collection.query.filter(Collection.id.in_(collection_ids)).all()
        video_model.collections.extend(collections)

    if title or collections:
        db_session.commit()

    return 'success'


@videos.route('/<int:video_id>', methods=['DELETE'])
def destroy(video_id):
    # Get video model
    video_model = find_or_404(Video, video_id)
    artist_id = video_model.artist_id
    video_filename = video_model.video_filename
    poster_filename = video_model.poster_filename

    # Delete model
    db_session.delete(video_model)
    db_session.commit()

    # Remove associated video files
    video_storage_path = video_model.storage_path(videos.root_path, video_filename)
    poster_storage_path = video_model.storage_path(videos.root_path, poster_filename, to_video=False)

    if os.path.isfile(video_storage_path):
        os.remove(video_storage_path)

    if os.path.isfile(poster_storage_path):
        os.remove(poster_storage_path)

    if not artist_id:
        return 'success'

    # Evaluate whether to delete associated Artist model
    artist_model = Artist.query.get(artist_id)

    if not artist_model.videos:
        db_session.delete(artist_model)
        db_session.commit()

    return 'success'
