from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from flask_uploads import UploadSet, configure_uploads

from config import Config

archives = UploadSet('archives', 'zip')
db = SQLAlchemy()
migrate = Migrate()
search = Search(db=db)
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message = 'You need to be logged in!'
login_manager.login_message_category = 'warning'
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    search.init_app(app)
    configure_uploads(app, archives)

    # Blueprints Import
    from .main import main
    from .user import user
    from .project import project
    from .errors import errors

    with app.app_context():
        app.register_blueprint(user)
        app.register_blueprint(main)
        app.register_blueprint(project)
        app.register_blueprint(errors)
        return app
