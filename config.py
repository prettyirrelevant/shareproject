import os
from os import path

from dotenv import load_dotenv

project_dir = path.join(path.dirname(__file__), "projects")
if not path.exists(project_dir):
    os.mkdir(project_dir)

# Load env variables
basedir = path.abspath(path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    FLASK_APP = os.environ.get("FLASK_APP")
    FLASK_ENV = os.environ.get("FLASK_ENV")
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # FLASKSQLALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///shareproject.db"

    # Flask-Uploads
    UPLOADED_ARCHIVES_DEST = project_dir
    UPLOADED_ARCHIVES_URL = "localhost:5000/projects/"

    WHOOSH_BASE = os.path.join(basedir, "search.db")

    # Msearch Config
    MSEARCH_INDEX_NAME = "msearch"
    MSEARCH_BACKEND = "whoosh"
    MSEARCH_PRIMARY_KEY = "id"
    MSEARCH_ENABLE = True


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
