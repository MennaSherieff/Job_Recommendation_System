from app import db
from flask_login import UserMixin
from datetime import datetime


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
    raw_text_path = db.Column(db.String(255), nullable=True)  # Path to stored cleaned text
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    recommendations = db.relationship('Recommendation', backref='cv', lazy=True)
    features = db.relationship('CVFeature', backref='cv', lazy=True, uselist=False)


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)
    video_file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    recommendations = db.relationship('Recommendation', backref='video', lazy=True)
    features = db.relationship('VideoFeature', backref='video', lazy=True, uselist=False)


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    job_url = db.Column(db.String(500), nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    recommendations = db.relationship('Recommendation', backref='job', lazy=True)
    features = db.relationship('JobFeature', backref='job', lazy=True, uselist=False)


class Recommendation(db.Model):
    __tablename__ = "recommendation"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=True)

    score = db.Column(db.Float, nullable=False)
    match_ratio = db.Column(db.Float, nullable=True)  # Hard skill match ratio
    matched_weight = db.Column(db.Integer, nullable=True)  # Number of matched skills
    required_weight = db.Column(db.Integer, nullable=True)  # Total required skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
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
    skill_type = db.Column(db.String(50), nullable=True)  # 'hard' or 'soft'


class MissingSkill(db.Model):
    __tablename__ = "missing_skill"

    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(
        db.Integer,
        db.ForeignKey('recommendation.id'),
        nullable=False
    )
    skill_name = db.Column(db.String(255), nullable=False)
    skill_type = db.Column(db.String(50), nullable=True)  # 'hard' or 'soft'


# FEATURE TABLES - Store extracted features for fast retrieval

class CVFeature(db.Model):

    __tablename__ = "cv_feature"

    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id'), nullable=False, unique=True)

    # Extracted skills as JSON lists
    hard_skills = db.Column(db.JSON, nullable=False)  # List of hard skill names
    soft_skills = db.Column(db.JSON, nullable=False)  # List of soft skill names

    # Binary vectors for matching (aligned with master skill lists)
    hard_skills_vector = db.Column(db.JSON, nullable=False)  # Binary vector
    soft_skills_vector = db.Column(db.JSON, nullable=False)  # Binary vector

    # Metadata
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobFeature(db.Model):
    __tablename__ = "job_feature"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False, unique=True)

    # Required skills as JSON lists
    required_hard_skills = db.Column(db.JSON, nullable=False)
    required_soft_skills = db.Column(db.JSON, nullable=False)

    # Binary vectors for matching
    hard_skills_vector = db.Column(db.JSON, nullable=False)
    soft_skills_vector = db.Column(db.JSON, nullable=False)

    # Skill count for quick filtering
    skill_count = db.Column(db.Integer, nullable=False)

    # Metadata
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow)


class VideoFeature(db.Model):
    """Store CNN-extracted features from video for soft skill prediction."""
    __tablename__ = "video_feature"

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False, unique=True)

    # CNN Features (15 learned embeddings from trained CNN model)
    # These represent soft skills extracted from video analysis
    cnn_features = db.Column(db.JSON, nullable=False)  # Array of 15 floats
    # [feat_95, feat_69, feat_125, feat_20, feat_91, feat_68, feat_117,
    #  feat_76, feat_11, feat_88, feat_94, feat_27, feat_82, feat_78, feat_8]

    # Derived soft skill match score
    soft_skill_match_score = db.Column(db.Float, nullable=False)

    # Optional: Human-readable soft skills for display
    predicted_soft_skills = db.Column(db.JSON, nullable=True)
    # Example: {'communication': 0.85, 'confidence': 0.72, 'professionalism': 0.90}

    # Metadata
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow)
