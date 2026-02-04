import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from models import (
    Recommendation, MatchedSkill, MissingSkill, 
    CV, CVFeature, Job, JobFeature, VideoFeature, db
)
import joblib
from src.pipeline.feature_extraction import compute_match_features, MASTER_HARD_SKILLS, MASTER_SOFT_SKILLS


class RecommendationService:
    _model = None
    
    _model_features = [
        "match_ratio", "missing_required_skills_count", "required_skill_count", 
        "missing_soft_skills_count_new", "video_id", "feat_95", "feat_69", 
        "feat_125", "feat_20", "feat_91", "feat_68", "feat_117", "feat_76", 
        "feat_11", "feat_88", "feat_94", "feat_27", "feat_82", "feat_78", 
        "feat_8", "domain_Administrative", "domain_Analytics", "domain_Business", 
        "domain_Consulting", "domain_Creative", "domain_Engineering", 
        "domain_Finance", "domain_HR", "domain_IT", "domain_Management", 
        "domain_Operations", "domain_Research", "domain_Support"
    ]

    @classmethod
    def _load_models(cls):
        """Load Logistic Regression model."""
        if cls._model is None:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'logistic_regression_model.pkl')
            if os.path.exists(model_path):
                cls._model = joblib.load(model_path)

    @staticmethod
    def generate_recommendations(user_id: int, cv_id: int, top_n: int = 10, video_feature_id: Optional[int] = None) -> List[Dict]:
        """
        Generate job recommendations for a user based on their CV using the specific Logistic Regression model.
        """
        # CRITICAL: Force SQLAlchemy to forget cached objects from previous requests/processing
        db.session.expire_all()
        
        # Get CV and its features
        cv = CV.query.get(cv_id)
        if not cv or cv.user_id != user_id:
            raise ValueError(f"CV {cv_id} not found or doesn't belong to user {user_id}")
        
        cv_features = CVFeature.query.filter_by(cv_id=cv_id).first()
        if not cv_features:
            raise ValueError(f"Features not extracted for CV {cv_id}. Please process the CV first.")
        
        # Get video features
        from models import Video
        if video_feature_id:
            # Use specific ID passed from the upload process
            video_features = VideoFeature.query.get(video_feature_id)
            print(f"[INFO] Using specific video feature ID: {video_feature_id}")
        else:
            # Fallback to latest
            video_features = (VideoFeature.query.join(Video)
                             .filter(Video.user_id == user_id, Video.status == 'completed')
                             .order_by(Video.uploaded_at.desc()).first())
            print("[INFO] No specific video feature ID provided, using latest completed.")

        if video_features:
            # Ensure the object is fresh from the DB
            db.session.refresh(video_features)
        
        # Get all active jobs with features
        jobs = Job.query.filter_by(is_active=True).all()
        
        RecommendationService._load_models()
        recommendations = []
        
        for job in jobs:
            if not job.features:
                continue
            
            # Compute basic match metrics
            match_result = RecommendationService._compute_match(cv_features, job.features)
            
            # Use model for scoring if available
            if RecommendationService._model:
                feature_dict = RecommendationService._prepare_features(
                    match_result, job, video_features
                )
                
                # Align features with training columns
                X = pd.DataFrame([feature_dict])
                
                # Add missing columns as zeros and ensure order
                for col in RecommendationService._model_features:
                    if col not in X.columns:
                        X[col] = 0
                
                X = X[RecommendationService._model_features]
                
                # Model Score (Probability of class 1)
                # score = 0.6 * model + 0.4 * ratio
                score = 0.6 * (RecommendationService._model.predict_proba(X)[0, 1] * 100) + 0.4 * (match_result['match_ratio'] * 100)
            else:
                # Fallback to match ratio
                score = match_result['match_ratio'] * 100
            
            # Store recommendation in database
            recommendation = Recommendation(
                user_id=user_id,
                job_id=job.id,
                cv_id=cv_id,
                # Fix: link to the Video.id, not the VideoFeature.id
                video_id=video_features.video_id if video_features else None,
                score=score,
                match_ratio=match_result['match_ratio'],
                matched_weight=match_result['matched_weight'],
                required_weight=match_result['required_weight']
            )
            db.session.add(recommendation)
            db.session.flush()
            
            # Store matched/missing skills
            RecommendationService._store_skills(recommendation.id, match_result)
            
            recommendations.append({
                'recommendation_id': recommendation.id,
                'job_id': job.id,
                'job_title': job.title,
                'company': job.company,
                'location': job.location,
                'domain': job.domain,
                'job_url': job.job_url,
                'score': score,
                'match_ratio': match_result['match_ratio'],
                'matched_skills_count': len(match_result['matched_hard_skills']) + len(match_result['matched_soft_skills']),
                'missing_skills_count': len(match_result['missing_hard_skills']) + len(match_result['missing_soft_skills'])
            })
        
        db.session.commit()
        
        # Sort by score (highest first) and return top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]

    @staticmethod
    def _prepare_features(match_result: Dict, job: Job, video_features: Optional[VideoFeature]) -> Dict:
        """
        Construct the feature dictionary for the ML model.
        """
        # Domain mapping for model consistency
        DOMAIN_MAPPING = {
            "finance": "domain_Finance",
            "engineering": "domain_Engineering", 
            "it": "domain_IT",
            "operations": "domain_Operations",
            "hr": "domain_HR",
            "accounting": "domain_Finance",
            "other": "domain_Administrative"
        }
        
        features = {
            'match_ratio': match_result['match_ratio'],
            'missing_required_skills_count': match_result['missing_required_skills_count'],
            'required_skill_count': match_result['required_skill_count'],
            'missing_soft_skills_count_new': len(match_result.get('missing_soft_skills', [])),
            'video_id': video_features.id if video_features else 0
        }
        
        # Add CNN features (feat_...)
        cnn_feats = video_features.cnn_features if video_features and video_features.cnn_features else {}
        # The model expects specific feat_ indices: 95, 69, 125, 20, 91, 68, 117, 76, 11, 88, 94, 27, 82, 78, 8
        target_feats = [95, 69, 125, 20, 91, 68, 117, 76, 11, 88, 94, 27, 82, 78, 8]
        for i in target_feats:
            feat_name = f'feat_{i}'
            features[feat_name] = cnn_feats.get(feat_name, 0.0)
            
        # Add one-hot encoded domains
        domain_lower = job.domain.lower()
        mapped_domain = DOMAIN_MAPPING.get(domain_lower, "domain_Administrative")
        
        all_domains = ["Administrative", "Analytics", "Business", "Consulting", "Creative", "Engineering", "Finance", "HR", "IT", "Management", "Operations", "Research", "Support"]
        for dom in all_domains:
            col_name = f"domain_{dom}"
            features[col_name] = 1 if col_name == mapped_domain else 0
            
        return features

    @staticmethod
    def _store_skills(recommendation_id: int, match_result: Dict):
        for skill_name in match_result['matched_hard_skills']:
            db.session.add(MatchedSkill(recommendation_id=recommendation_id, skill_name=skill_name, skill_type='hard'))
        for skill_name in match_result['matched_soft_skills']:
            db.session.add(MatchedSkill(recommendation_id=recommendation_id, skill_name=skill_name, skill_type='soft'))
        for skill_name in match_result['missing_hard_skills']:
            db.session.add(MissingSkill(recommendation_id=recommendation_id, skill_name=skill_name, skill_type='hard'))
        for skill_name in match_result['missing_soft_skills']:
            db.session.add(MissingSkill(recommendation_id=recommendation_id, skill_name=skill_name, skill_type='soft'))

    @staticmethod
    def _compute_match(cv_features: CVFeature, job_features: JobFeature) -> Dict:
        """
        Compute matching metrics between CV and job features.
        """
        # Use the pipeline function to compute match
        matched_weight, required_weight, match_ratio, missing_count, missing_hard, missing_soft = compute_match_features(
            cv_features.hard_skills_vector,
            job_features.hard_skills_vector,
            cv_features.soft_skills_vector,
            job_features.soft_skills_vector
        )
        
        # Identify matched skills (skills present in both CV and JD)
        matched_hard_skills = [
            MASTER_HARD_SKILLS[i]
            for i in range(len(cv_features.hard_skills_vector))
            if cv_features.hard_skills_vector[i] and job_features.hard_skills_vector[i]
        ]
        
        matched_soft_skills = [
            MASTER_SOFT_SKILLS[i]
            for i in range(len(cv_features.soft_skills_vector))
            if cv_features.soft_skills_vector[i] and job_features.soft_skills_vector[i]
        ]
        
        return {
            'matched_weight': matched_weight,
            'required_weight': required_weight,
            'match_ratio': match_ratio,
            'missing_required_skills_count': missing_count,
            'required_skill_count': required_weight,
            'matched_hard_skills': matched_hard_skills,
            'matched_soft_skills': matched_soft_skills,
            'missing_hard_skills': missing_hard,
            'missing_soft_skills': missing_soft
        }
    
    @staticmethod
    def get_recommendation_details(recommendation_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific recommendation.
        """
        recommendation = Recommendation.query.get(recommendation_id)
        if not recommendation:
            return None
        
        # Get matched skills
        matched_skills = MatchedSkill.query.filter_by(recommendation_id=recommendation_id).all()
        matched_hard = [s.skill_name for s in matched_skills if s.skill_type == 'hard']
        matched_soft = [s.skill_name for s in matched_skills if s.skill_type == 'soft']
        
        # Get missing skills
        missing_skills = MissingSkill.query.filter_by(recommendation_id=recommendation_id).all()
        missing_hard = [s.skill_name for s in missing_skills if s.skill_type == 'hard']
        missing_soft = [s.skill_name for s in missing_skills if s.skill_type == 'soft']
        
        return {
            'id': recommendation.id,
            'job_id': recommendation.job_id,
            'job_title': recommendation.job.title,
            'company': recommendation.job.company,
            'location': recommendation.job.location,
            'domain': recommendation.job.domain,
            'description': recommendation.job.description,
            'score': recommendation.score,
            'match_ratio': recommendation.match_ratio,
            'matched_weight': recommendation.matched_weight,
            'required_weight': recommendation.required_weight,
            'matched_hard_skills': matched_hard,
            'matched_soft_skills': matched_soft,
            'missing_hard_skills': missing_hard,
            'missing_soft_skills': missing_soft,
            'created_at': recommendation.created_at.isoformat() if recommendation.created_at else None
        }
    
    @staticmethod
    def get_user_recommendations(user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all recommendations for a user.
        """
        query = Recommendation.query.filter_by(user_id=user_id).order_by(Recommendation.score.desc())
        
        if limit:
            query = query.limit(limit)
        
        recommendations = query.all()
        
        return [
            {
                'id': rec.id,
                'job_id': rec.job_id,
                'job_title': rec.job.title,
                'company': rec.job.company,
                'location': rec.job.location,
                'domain': rec.job.domain,
                'score': rec.score,
                'match_ratio': rec.match_ratio,
                'matched_skills_count': rec.matched_weight,
                'missing_skills_count': rec.required_weight - rec.matched_weight if rec.required_weight else 0,
                'created_at': rec.created_at.isoformat() if rec.created_at else None
            }
            for rec in recommendations
        ]
    
    @staticmethod
    def clear_user_recommendations(user_id: int, cv_id: Optional[int] = None) -> int:
        """
        Clear existing recommendations for a user.
        """
        query = Recommendation.query.filter_by(user_id=user_id)
        
        if cv_id:
            query = query.filter_by(cv_id=cv_id)
        
        count = query.count()
        query.delete()
        db.session.commit()
        
        return count

    @staticmethod
    def generate_manual_match(cv_skills: List[str], job_skills: List[str], domain: str) -> Dict:
        """
        Generate a manual match score for POC purposes.
        """
        # Calculate simple match ratio
        cv_set = set([s.lower() for s in cv_skills])
        job_set = set([s.lower() for s in job_skills])
        
        if not job_set:
            match_ratio = 0.0
        else:
            matched = cv_set.intersection(job_set)
            match_ratio = len(matched) / len(job_set)
            
        score = match_ratio * 100
            
        return {
            'cv_skills': cv_skills,
            'job_skills': job_skills,
            'domain': domain,
            'score': round(score, 2),
            'match_ratio': round(match_ratio, 2),
            'matched_skills': list(cv_set.intersection(job_set)),
            'missing_skills': list(job_set - cv_set)
        }
