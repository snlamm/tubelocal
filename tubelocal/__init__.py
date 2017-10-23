import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'tubelocal.db')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True, echo='debug')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
import tubelocal.models
from tubelocal.views.collections import collections
from tubelocal.views.videos import videos
from tubelocal.views.artists import artists
migrate = Migrate(app, Base)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


app.register_blueprint(collections)
app.register_blueprint(videos)
app.register_blueprint(artists)
