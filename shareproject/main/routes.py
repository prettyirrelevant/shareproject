from datetime import datetime, timedelta

from flask import g, request, render_template

from . import main
from ..forms import SearchForm
from ..models import Project


@main.before_app_request
def before_request():
    g.previous_url = request.referrer
    g.search_form = SearchForm()


@main.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    yesterday = datetime.today() - timedelta(days=1)
    projects = (
        Project.query.filter(Project.created >= yesterday)
        .order_by(Project.created.desc())
        .paginate(page=page, per_page=2)
    )

    return render_template("index.html", title="Home", projects=projects)
