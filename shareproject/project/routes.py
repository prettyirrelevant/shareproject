import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import humanize
from flask import url_for, render_template, flash, g, redirect, request, abort
from flask_login import login_required, current_user
from slugify import slugify

from . import project
from .utils import (
    save_zip_project,
    delete_zip_project,
    breadcrumbs_create,
    unzip_project,
)
from .. import db
from ..forms import ProjectForm, ProjectUpdateForm
from ..models import Project
from ..main.utils import add_to_db

separator = os.sep


@project.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = ProjectForm()
    if form.validate_on_submit():
        slug = slugify(form.name.data)

        file_path = save_zip_project()

        new_file_path = os.path.join(str(Path(file_path).parent), slug)

        # unzipping the zipped project file
        unzip_project(file_path, new_file_path)

        # creates a new instance of 'Project'
        new_project = Project(
            name=form.name.data, user_id=current_user.id, path=new_file_path, slug=slug
        )

        add_to_db(new_project)

        # deletes the uploaded zip file after unzipping.
        delete_zip_project(file_path)

        flash("Project added successfully!", "info")
        return redirect(url_for("main.index"))
    return render_template("add.html", title="Add Project", form=form)


@project.route("/search")
def search():
    if not g.search_form.validate():
        return redirect(url_for("main.index"))

    page = request.args.get("page", 1, type=int)
    projects = Project.query.msearch(
        g.search_form.q.data, fields=["name", "description"], limit=50
    ).paginate(page=page, per_page=2)

    next_url = (
        url_for("project.search", page=projects.next_num, q=g.search_form.q.data)
        if projects.has_next
        else None
    )

    prev_url = (
        url_for("project.search", page=projects.prev_num, q=g.search_form.q.data)
        if projects.has_prev
        else None
    )

    return render_template(
        "search.html",
        title="Search",
        projects=projects.items,
        next_url=next_url,
        prev_url=prev_url,
        total=projects.total,
    )


# DISPLAY PROJECT ROUTE
@project.route("/project/<path:proj_path>", methods=["POST", "GET"])
def view_project(proj_path):
    slug = proj_path.split("/")[0]
    project = Project.query.filter_by(slug=slug).first_or_404()
    path = project.path
    contents = []
    breadcrumbs = []
    req_path = os.path.join(os.path.dirname(path), proj_path)
    form = ProjectUpdateForm()
    if form.validate_on_submit():
        project.description = form.description.data
        db.session.commit()
        return redirect(url_for("project.view_project", proj_path=proj_path))

    elif request.method == "GET":
        form.name.data = project.name
        form.description.data = project.description

        if os.path.exists(req_path):
            if os.path.isdir(req_path):
                with os.scandir(req_path) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            contents.append(
                                {
                                    "path": separator.join(
                                        os.path.relpath(entry.path).split("/")[1:]
                                    ),
                                    "name": entry.name,
                                }
                            )
                        else:
                            contents.append(
                                {
                                    "path": separator.join(
                                        os.path.relpath(entry.path).split("/")[1:]
                                    ),
                                    "name": entry.name,
                                    "last_modified": humanize.naturaltime(
                                        datetime.fromtimestamp(entry.stat().st_mtime)
                                        - timedelta(seconds=1)
                                    ),
                                    "size": humanize.naturalsize(
                                        entry.stat().st_size, binary=True
                                    ),
                                }
                            )
            else:
                with open(req_path) as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError as e:
                        return "Unable to open such file format"

                # creates breadcrumbs for the url path given. 'breadcrumbs' is the path. 'br' is the path name
                breadcrumbs_create(proj_path, breadcrumbs)
                return render_template(
                    "view_file.html",
                    content=content,
                    project=project,
                    file=proj_path,
                    title=project.name,
                    breadcrumbs=breadcrumbs,
                    br=proj_path.split("/"),
                )
        else:
            abort(404)
        # creates breadcrumbs for the url path given. 'breadcrumbs' is the path. 'br' is the path name
        breadcrumbs_create(proj_path, breadcrumbs)

    return render_template(
        "view_project.html",
        contents=contents,
        project=project,
        title=project.name,
        form=form,
        breadcrumbs=breadcrumbs,
        br=proj_path.split("/"),
    )


@project.route("/project/<path:proj_path>/save", methods=["POST"])
def save_file(proj_path):
    slug = proj_path.split("/")[0]
    project = Project.query.filter_by(slug=slug).first_or_404()
    path = project.path
    if request.method == "POST":
        if current_user.is_authenticated and current_user.id == project.user_id:
            file_path = os.path.join(os.path.dirname(path), proj_path)
            data = request.form.get("aceUpdate")
            with open(file_path, "w", newline="") as f:
                f.write(data)
        else:
            abort(403)

    return redirect(url_for("project.view_project", proj_path=proj_path))


@project.route("/project/<path:proj_path>/delete")
def delete_file_dir(proj_path):
    slug = proj_path.split("/")[0]
    project = Project.query.filter_by(slug=slug).first_or_404()
    path = project.path
    if current_user.is_authenticated and current_user.id == project.user_id:
        file_path = os.path.join(os.path.dirname(path), proj_path)
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
        except OSError as e:
            flash(str(e), "error")
            return redirect(request.referrer)
        else:
            return redirect(request.referrer)

    else:
        print("Here")
        abort(403)


@project.route("/project/<path:proj_path>/delete_project")
def delete_project(proj_path):
    slug = proj_path.split("/")[0]
    project = Project.query.filter_by(slug=slug).first_or_404()
    path = project.path
    if current_user.is_authenticated and current_user.id == project.user_id:
        file_path = os.path.join(os.path.dirname(path), proj_path)
        try:
            shutil.rmtree(file_path)
            db.session.delete(project)
            db.session.commit()
        except OSError as e:
            return str(e)

    else:
        abort(403)

    return redirect(url_for("user.profile", username=current_user.username))


@project.route("/<project_slug>/like")
def like(project_slug):
    if current_user.is_authenticated:
        project = Project.query.filter_by(slug=project_slug).first()
        if project is None:
            flash("Project not found", "danger")
            return redirect(request.referrer)

        project.like(current_user)
        db.session.commit()
        flash(f"You liked {project.name}", "success")

        # redirects to the previous url
        return redirect(g.previous_url)
    else:
        flash("You need to be logged in to like a project", "info")
        return redirect(url_for("user.login"))


@project.route("/<project_slug>/unlike")
def unlike(project_slug):
    if current_user.is_authenticated:

        project = Project.query.filter_by(slug=project_slug).first()
        if project is None:
            flash("Project not found", "danger")
            return redirect(request.referrer)

        project.unlike(current_user)
        db.session.commit()
        flash(f"You unliked {project.name}", "success")
        # redirects to the previous url
        return redirect(g.previous_url)

    else:
        flash("You need to be logged in to unlike a project", "info")
        return redirect(url_for("user.login"))
