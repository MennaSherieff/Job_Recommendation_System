import os
from typing import Dict, List, Optional
from pathlib import Path as FilePath
from datetime import datetime
from models import CV, CVFeature, VideoFeature, db
from src.pipeline.feature_extraction import extract_cv_features


class CVService:
    """Service for processing CVs and extracting features."""
    
    @staticmethod
    def process_cv(cv_id: int) -> Dict:
        """
        Process a CV: extract features and store them in the database.
        
        Args:
            cv_id: ID of the CV record in database
            
        Returns:
            Dictionary containing processing results and extracted features
            
        Raises:
            ValueError: If CV not found or file doesn't exist
        """
        # Get CV record
        cv = CV.query.get(cv_id)
        if not cv:
            raise ValueError(f"CV with ID {cv_id} not found")
        
        # Update status to processing
        cv.status = 'processing'
        db.session.commit()
        
        try:
            # Read CV text from file
            cv_file_path = FilePath(cv.cv_file_path)
            if not cv_file_path.exists():
                raise ValueError(f"CV file not found: {cv.cv_file_path}")
            
            cv_text = cv_file_path.read_text(encoding='utf-8')
            
            # Extract features using pipeline
            features = extract_cv_features(cv_text)
            
            # Check if features already exist (update) or create new
            cv_feature = CVFeature.query.filter_by(cv_id=cv_id).first()
            
            if cv_feature:
                # Update existing features
                cv_feature.hard_skills = features['hard_skills']
                cv_feature.soft_skills = features['soft_skills']
                cv_feature.hard_skills_vector = features['hard_vector']
                cv_feature.soft_skills_vector = features['soft_vector']
                cv_feature.extracted_at = datetime.utcnow()
            else:
                # Create new feature record
                cv_feature = CVFeature(
                    cv_id=cv_id,
                    hard_skills=features['hard_skills'],
                    soft_skills=features['soft_skills'],
                    hard_skills_vector=features['hard_vector'],
                    soft_skills_vector=features['soft_vector']
                )
                db.session.add(cv_feature)
            
            # Update CV status to completed
            cv.status = 'completed'
            db.session.commit()
            
            return {
                'success': True,
                'cv_id': cv_id,
                'hard_skills': features['hard_skills'],
                'soft_skills': features['soft_skills'],
                'hard_skills_count': len(features['hard_skills']),
                'soft_skills_count': len(features['soft_skills'])
            }
            
        except Exception as e:
            # Update status to failed
            cv.status = 'failed'
            db.session.commit()
            raise e
    
    @staticmethod
    def get_cv_features(cv_id: int) -> Optional[Dict]:
        """
        Retrieve extracted features for a CV.
        
        Args:
            cv_id: ID of the CV record
            
        Returns:
            Dictionary containing CV features or None if not found
        """
        cv_feature = CVFeature.query.filter_by(cv_id=cv_id).first()
        
        if not cv_feature:
            return None
        
        return {
            'cv_id': cv_id,
            'hard_skills': cv_feature.hard_skills,
            'soft_skills': cv_feature.soft_skills,
            'hard_skills_vector': cv_feature.hard_skills_vector,
            'soft_skills_vector': cv_feature.soft_skills_vector,
            'extracted_at': cv_feature.extracted_at.isoformat() if cv_feature.extracted_at else None
        }
    
    @staticmethod
    def get_cv_status(cv_id: int) -> Optional[str]:
        """
        Get the processing status of a CV.
        
        Args:
            cv_id: ID of the CV record
            
        Returns:
            Status string ('pending', 'processing', 'completed', 'failed') or None
        """
        cv = CV.query.get(cv_id)
        return cv.status if cv else None
    
    @staticmethod
    def list_user_cvs(user_id: int) -> List[Dict]:
        """
        List all CVs uploaded by a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of CV dictionaries with basic info
        """
        cvs = CV.query.filter_by(user_id=user_id).order_by(CV.uploaded_at.desc()).all()
        
        return [
            {
                'id': cv.id,
                'uploaded_at': cv.uploaded_at.isoformat() if cv.uploaded_at else None,
                'status': cv.status,
                'has_features': cv.features is not None
            }
            for cv in cvs
        ]

    @staticmethod
    def delete_cv(cv_id: int, user_id: int) -> bool:
        """
        Delete a CV and all its associated data.
        """
        cv = CV.query.filter_by(id=cv_id, user_id=user_id).first()
        if not cv:
            return False
            
        # Delete associated features
        CVFeature.query.filter_by(cv_id=cv_id).delete()
        
        # Delete associated recommendations and their skills
        from models import Recommendation, MatchedSkill, MissingSkill,Video
        recommendations = Recommendation.query.filter_by(cv_id=cv_id).all()
        for rec in recommendations:
            MatchedSkill.query.filter_by(recommendation_id=rec.id).delete()
            MissingSkill.query.filter_by(recommendation_id=rec.id).delete()
            db.session.delete(rec)
            
    # Delete videos + video features (for this user)
        # videos = Video.query.filter_by(user_id=user_id).all()
        # for video in videos:
        # # delete video features first
        #     VideoFeature.query.filter_by(video_id=video.id).delete()
        #     db.session.delete(video)

        # Delete the CV file if it exists
        try:
            if cv.cv_file_path and os.path.exists(cv.cv_file_path):
                os.remove(cv.cv_file_path)
        except Exception as e:
            print(f"Warning: Could not delete CV file: {e}")
            
        # Delete the CV record
        db.session.delete(cv)
        db.session.commit()
        
        return True
