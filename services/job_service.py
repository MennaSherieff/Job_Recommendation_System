"""
Job Service - Handles job management and feature extraction.
"""
from typing import Dict, List, Optional
from datetime import datetime
from models import Job, JobFeature, db
from pipeline.feature_extraction import extract_jd_features


class JobService:
    @staticmethod
    def create_job(title: str, description: str, domain: str, 
                   company: Optional[str] = None, location: Optional[str] = None, job_url: Optional[str] = None) -> int:
        """
        Create a new job listing and extract its features.
        """
        # Create job record
        job = Job(
            title=title,
            description=description,
            domain=domain,
            company=company,
            location=location,
            job_url=job_url,
            is_active=True
        )
        db.session.add(job)
        db.session.flush()  # Get job.id
        # Extract features from job description
        features = extract_jd_features(description)
        
        # Create job feature record
        job_feature = JobFeature(
            job_id=job.id,
            required_hard_skills=features['required_hard_skills'],
            required_soft_skills=features['required_soft_skills'],
            hard_skills_vector=features['hard_vector'],
            soft_skills_vector=features['soft_vector'],
            skill_count=features['skill_count']
        )
        db.session.add(job_feature)
        db.session.commit()
        
        return job.id
    
    @staticmethod
    def get_job(job_id: int) -> Optional[Dict]:
        """
        Get job details including features.
        """
        job = Job.query.get(job_id)
        if not job:
            return None
        
        result = {
            'id': job.id,
            'job_url':job.job_url,
            'title': job.title,
            'description': job.description,
            'domain': job.domain,
            'company': job.company,
            'location': job.location,
            'posted_at': job.posted_at.isoformat() if job.posted_at else None,
            'is_active': job.is_active
        }
        
        # Add features if available
        if job.features:
            result['required_hard_skills'] = job.features.required_hard_skills
            result['required_soft_skills'] = job.features.required_soft_skills
            result['skill_count'] = job.features.skill_count
        
        return result
    
    @staticmethod
    def get_job_features(job_id: int) -> Optional[Dict]:
        """
        Get extracted features for a job.
        """
        job_feature = JobFeature.query.filter_by(job_id=job_id).first()
        
        if not job_feature:
            return None
        
        return {
            'job_id': job_id,
            'required_hard_skills': job_feature.required_hard_skills,
            'required_soft_skills': job_feature.required_soft_skills,
            'hard_skills_vector': job_feature.hard_skills_vector,
            'soft_skills_vector': job_feature.soft_skills_vector,
            'skill_count': job_feature.skill_count,
            'extracted_at': job_feature.extracted_at.isoformat() if job_feature.extracted_at else None
        }
    
    @staticmethod
    def list_active_jobs(limit: Optional[int] = None) -> List[Dict]:
        """
        List all active jobs.
        """
        query = Job.query.filter_by(is_active=True).order_by(Job.posted_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        jobs = query.all()
        
        return [
            {
                'id': job.id,
                'title': job.title,
                'domain': job.domain,
                'company': job.company,
                'location': job.location,
                'posted_at': job.posted_at.isoformat() if job.posted_at else None,
                'skill_count': job.features.skill_count if job.features else 0
            }
            for job in jobs
        ]
    
    @staticmethod
    def deactivate_job(job_id: int) -> bool:
        """
        Deactivate a job listing.
        """
        job = Job.query.get(job_id)
        if not job:
            return False
        
        job.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def refresh_job_features(job_id: int) -> bool:
        """
        Re-extract features for an existing job and update the database.
        """
        job = Job.query.get(job_id)
        if not job:
            return False
            
        # Extract features from job description
        features = extract_jd_features(job.description)
        
        # Update or create job feature record
        job_feature = JobFeature.query.filter_by(job_id=job_id).first()
        
        if job_feature:
            job_feature.required_hard_skills = features['required_hard_skills']
            job_feature.required_soft_skills = features['required_soft_skills']
            job_feature.hard_skills_vector = features['hard_vector']
            job_feature.soft_skills_vector = features['soft_vector']
            job_feature.skill_count = features['skill_count']
            job_feature.extracted_at = datetime.utcnow()
        else:
            job_feature = JobFeature(
                job_id=job_id,
                required_hard_skills=features['required_hard_skills'],
                required_soft_skills=features['required_soft_skills'],
                hard_skills_vector=features['hard_vector'],
                soft_skills_vector=features['soft_vector'],
                skill_count=features['skill_count']
            )
            db.session.add(job_feature)
            
        db.session.commit()
        return True
