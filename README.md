# tubelocal

A JSON backend api to download and organize youtube videos for viewing offline. Built in Flask and Python 3.

### Components
- Handle video downloads with pafy. Require only Youtube urls as input.
- Assign videos to multiple collections and vice versa. Autogenerate (and delete) video-artists as videos are created and deleted.
- Provide jsonified CRUD logic for videos and collections, and read logic for artists.
- Leverage SQLAlchemy for the SQL toolkit and ORM. Run migrations through alembic.

### Local Setup
```bash
virtualenv venv
. venv/bin/activate
pip install Flask sqlalchemy flask_migrate pafy youtube-dl
export FLASK_APP=tubelocal
flask db upgrade
flask run
```

### License
MIT