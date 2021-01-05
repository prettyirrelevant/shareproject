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
    SECRET_KEY = "E+W4trE/JZ5pRupZEaSe/lUJ0Rh7MlqJxHZVzZF65HM="
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
    ENV = "production"
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
