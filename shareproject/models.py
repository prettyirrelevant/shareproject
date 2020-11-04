from datetime import datetime

from flask_login import UserMixin

from shareproject import login_manager, db, bcrypt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


project_likes = db.Table(
    "project_likes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    profile_path = db.Column(db.String(180), nullable=False)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship("Project", backref="author", lazy=True)

    def __init__(self, username, email, password, profile_path="default.png"):
        self.username = username
        self.email = email
        self.password = self.get_pw_hash(password)
        self.profile_path = profile_path

    def get_pw_hash(self, password):
        pw = bcrypt.generate_password_hash(password)
        return pw.decode("utf-8")

    def check_pw_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Project(db.Model):
    __tablename__ = "project"
    __searchable__ = ["description", "name"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False, default="Just another project!")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug = db.Column(db.String(150), nullable=False)
    project_liked = db.relationship(
        "User",
        secondary=project_likes,
        backref=db.backref("liked_projects", lazy="dynamic"),
        lazy="dynamic",
    )
    path = db.Column(db.String(180), nullable=False)

    def already_liked(self, user):
        return self.project_liked.filter(User.id == user.id).count() > 0

    def like(self, user):
        if not self.already_liked(user):
            self.project_liked.append(user)
            db.session.commit()
            return self

    def unlike(self, user):
        if self.already_liked(user):
            self.project_liked.remove(user)
            db.session.commit()
            return self
