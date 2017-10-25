from tubelocal import Blueprint, db_session, request, jsonify
from ..models import Collection, Video, find_or_404

collections = Blueprint('collections', 'collections', url_prefix='/collections')


@collections.route('/', methods=['GET'])
def index():
    models = db_session.query(Collection).all()
    return jsonify([model.toDict() for model in models])


@collections.route('/<int:collection_id>', methods=['GET'])
def show(collection_id):
    return find_or_404(Collection, collection_id).toDict(to_json=True)


@collections.route('/', methods=['POST'])
def create():
    name = None

    try:
        name = request.form['name']
    except Exception as err:
        raise AttributeError({'name': 'name is required'}, err)

    if Collection.query.filter(Collection.name == name).first():
        raise Exception('Collection name already exists')

    collection = Collection(name=name)
    db_session.add(collection)
    db_session.commit()

    return collection.toDict(to_json=True)


@collections.route('/<int:collection_id>', methods=['PATCH'])
def update(collection_id):
    collection_model = find_or_404(Collection, collection_id)

    name = request.form.get('name', None)
    video_ids_string = request.form.get('video_ids', None)
    video_ids = video_ids_string.split(',') if video_ids_string else []

    if name:
        collection_model.name = name

    videos = None

    # Assign multiple videos
    if video_ids:
        videos = Video.query.filter(Video.id.in_(video_ids)).all()
        collection_model.videos.extend(videos)

    if name or videos:
        db_session.commit()

    return 'success'


@collections.route('/<int:collection_id>', methods=['DELETE'])
def destroy(collection_id):
    collection_model = find_or_404(Collection, collection_id)
    db_session.delete(collection_model)
    db_session.commit()

    return 'success'
