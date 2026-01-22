from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(125), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    # Relationships
    cvs = db.relationship('CV', backref='user', lazy=True)
    videos = db.relationship('Video', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)


class CV(db.Model):
    __tablename__ = "cv"

    id = db.Column(db.Integer, primary_key=True)
    cv_file_path = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    recommendations = db.relationship('Recommendation', backref='cv', lazy=True)


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)
    video_file_path = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    recommendations = db.relationship('Recommendation', backref='video', lazy=True)


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(255), nullable=False)

    recommendations = db.relationship('Recommendation', backref='job', lazy=True)


class Recommendation(db.Model):
    __tablename__ = "recommendation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=True)

    score = db.Column(db.Float, nullable=False)

    matched_skills = db.relationship('MatchedSkill', backref='recommendation', lazy=True)
    missing_skills = db.relationship('MissingSkill', backref='recommendation', lazy=True)


class MatchedSkill(db.Model):
    __tablename__ = "matched_skill"

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(
        db.Integer,
        db.ForeignKey('recommendation.id'),
        nullable=False
    )
    skill_name = db.Column(db.String(255), nullable=False)


class MissingSkill(db.Model):
    __tablename__ = "missing_skill"

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(
        db.Integer,
        db.ForeignKey('recommendation.id'),
        nullable=False
    )
    skill_name = db.Column(db.String(255), nullable=False)
