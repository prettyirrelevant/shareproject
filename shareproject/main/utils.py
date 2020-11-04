from .. import db
from flask import redirect, url_for
from flask_login import current_user


def add_to_db(object_instance):
    db.session.add(object_instance)
    db.session.commit()


def redirect_if_authenticated():
    if current_user.is_authenticated:
        return redirect(url_for("user.login"))
