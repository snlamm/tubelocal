import os
import datetime
from tubelocal import Blueprint, request, jsonify, db_session, abort
from ..models import Video, Artist
import pafy
import urllib.request

videos = Blueprint('videos', 'videos', url_prefix='/videos')


@videos.route('/', methods=['GET'])
def index():
    models = db_session.query(Video).all()
    return jsonify([model.toDict() for model in models])


@videos.route('/<int:video_id>', methods=['GET'])
def show(video_id):
    video_model = Video.query.get(video_id)

    if not video_model:
        abort(404)

    return video_model.toDict(to_json=True)


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
        db_session.commit()

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
    filename = '%d-%d' % (vid_model.id, vid_model.created_at.timestamp())
    filepath = os.path.join(videos.root_path, 'tubelocal/storage')
    video_storage_path = os.path.join(filepath, 'videos/%s' % filename)
    poster_storage_path = os.path.join(filepath, 'posters/%s' % filename)

    # Attempt to download stream to filepath and update video model with it.
    # On error, delete downloads (and artist) if they were created
    try:
        # stream.download(quiet=False, filepath=video_storage_path)
        # urllib.request.urlretrieve(poster_url, poster_storage_path)
        vid_model.video_filename = filename
        vid_model.poster_filename = filename
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


# TODO update videos but don't allow changing artist. Allow assigning a collection
# @videos.route('/videos/<int:id>', methods=[ 'PATCH' ])
# def update():
#     return render_template('videos/create.html.j2')


# TODO allow deleting a video 
# @videos.route('/videos/<int:id>', methods=[ 'DELETE' ])
# def destroy():
#     return render_template('videos/create.html.j2')

# TODO allow bulk deleting videos
# TODO allow bulk assigning of videos to collections

