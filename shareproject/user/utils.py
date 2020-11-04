import secrets
import os
from flask import current_app as app
from flask_login import current_user
from PIL import Image


def save_picture(picture):
    random_name = secrets.token_hex(8)
    _, ext = os.path.splitext(picture.filename)
    picture_name = random_name + ext
    path = os.path.join(app.root_path, "static/profile_pics", picture_name)

    size = (300, 300)

    i = Image.open(picture)
    i.thumbnail(size)
    i.save(path)

    return picture_name


def delete_prev_profile_pic():
    # deletes previous profile picture
    if current_user.profile_path != "default.png":
        os.remove(
            os.path.join(
                app.root_path, "static/profile_pics", current_user.profile_path
            )
        )
