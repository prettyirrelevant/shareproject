from flask import request
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from shareproject import archives
from shareproject.models import User, Project


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message=f"You cannot leave ths field blank."),
            Length(min=4, message=f"Username must be at least 4 characters long."),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[
            Email(message=f"Email address is not valid."),
            DataRequired(message=f"You cannot leave this field blank."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(f"A password is required for login."),
            Length(min=6, message="Password must be at least 6 character long."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(f"You cannot leave ths field blank."),
            EqualTo("password", message="Passwords don't match."),
        ],
    )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already exists. Choose another one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email address already exists. Choose another one.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(f"You cannot leave ths field blank."), Length(min=4)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(f"You cannot leave ths field blank."), Length(min=6)],
    )
    remember = BooleanField("Remember Me")


class ProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message=f"You cannot leave ths field blank."),
            Length(min=4, message=f"Username must be at least 4 characters long."),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[
            Email(message=f"Email address is not valid."),
            DataRequired(message=f"You cannot leave this field blank."),
        ],
    )
    picture_upload = FileField(
        "Upload",
        validators=[
            FileAllowed("jpg jpe jpeg png gif svg bmp".split(), f"Picture formats only")
        ],
    )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "Email address already exists. Choose another one."
                )


class ProjectForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[DataRequired(f"You cannot leave ths field blank."), Length(min=5)],
    )
    file = FileField(
        "Upload",
        validators=[
            FileRequired(f"File must be uploaded."),
            FileAllowed(archives, "Zip format only!"),
        ],
    )

    def validate_name(self, name):
        project = Project.query.filter_by(name=name.data).first()
        if project:
            raise ValidationError(f"{name.data} is not available. Make another choice.")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class ProjectUpdateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
            Length(min=5, message="Field cannot be less than 5 characters."),
        ],
    )
