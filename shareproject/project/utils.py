import os
from .. import archives
from flask import request
from zipfile import ZipFile


def breadcrumbs_create(path, breadcrumbs):
    __ = []
    for _ in path.split("/"):
        __.append(_)
        breadcrumbs.append("/".join(__))


def save_zip_project():
    file = archives.save(request.files.get("file"))
    file_path = archives.path(file)

    return file_path


def unzip_project(path, new_path):
    with ZipFile(path) as zipProject:
        zipProject.extractall(new_path)


def delete_zip_project(path):
    os.remove(path)
