from flask import flash, url_for, redirect, render_template, request
from flask_login import login_user, logout_user

from . import user
from .. import db
from ..forms import RegistrationForm, LoginForm, ProfileForm
from ..models import User, Project
from ..main.utils import redirect_if_authenticated, add_to_db
from .utils import save_picture, delete_prev_profile_pic


@user.route("/register", methods=["GET", "POST"])
def register():
    redirect_if_authenticated()

    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        add_to_db(new_user)

        flash(
            "Your account has been created successfully. You can now login", "success"
        )
        return redirect(url_for("user.login"))

    return render_template("register.html", title="Register", form=form)


@user.route("/login", methods=["GET", "POST"])
def login():
    redirect_if_authenticated()

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_pw_hash(form.password.data):
            next_url = request.args.get("next")
            login_user(user, form.remember.data)

            flash("Login Successful", "success")
            return redirect(next_url) if next_url else redirect(url_for("main.index"))
        else:
            flash("Username or/and password incorrect!", "danger")

    return render_template("login.html", title="Login", form=form)


# PROFILE
@user.route("/<username>", methods=["GET", "POST"])
# @login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    projects = Project.query.filter_by(user_id=user.id)
    form = ProfileForm()

    page = request.args.get("page", 1, type=int)
    paginate_projects = projects.paginate(page=page, per_page=2)

    if form.validate_on_submit():
        if form.picture_upload.data:
            form_picture = request.files.get("picture_upload")
            # saves the picture uploaded and returns the filename
            picture_name = save_picture(form_picture)
            # checks if previous picture is 'default.png', if false it is deleted
            delete_prev_profile_pic()
            user.profile_path = picture_name

        user.email = form.email.data
        user.username = form.username.data
        db.session.commit()

        return redirect(url_for("user.profile", username=user.username))

    if request.method == "GET":
        form.email.data = user.email
        form.username.data = user.username

    # gets the path of the profile picture
    image_url = url_for("static", filename="profile_pics/" + user.profile_path)
    return render_template(
        "profile.html",
        title=user.username,
        image_url=image_url,
        form=form,
        projects=paginate_projects,
        user=user,
    )


# ADD PROJECT ROUTE


# LOGOUT ROUTE
@user.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("main.index"))
