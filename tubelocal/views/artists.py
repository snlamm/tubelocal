from tubelocal import Blueprint, jsonify, db_session
from ..models import Artist, find_or_404

artists = Blueprint('artists', 'artists', url_prefix='/artists')
# Users should not be able to delete or update artists


@artists.route('/', methods=['GET'])
def index():
    models = db_session.query(Artist).all()
    return jsonify([model.toDict(use_eager=False) for model in models])


@artists.route('/<int:artist_id>', methods=['GET'])
def show(artist_id):
    artist_model = find_or_404(Artist, artist_id)
    return artist_model.toDict(to_json=True)
