import pandas as pd
import os
import sys
# Add the project root to sys.path to import models and services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from services.job_service import JobService
from models import Job

def populate_jobs(csv_path, limit=100):
    app = create_app()
    with app.app_context():
        print(f"Reading job data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        df = df.fillna("")
        
        if limit:
            df = df.head(limit)
            
        print(f"Importing {len(df)} jobs...")
        
        count = 0
        for _, row in df.iterrows():
            # Check if job already exists by title and company to avoid duplicates
            existing_job = Job.query.filter_by(
                title=row['job_title'], 
                company=row['company']
            ).first()
            
            if existing_job:
                # Refresh features and update URL for existing job
                try:
                    existing_job.job_url = row['url']
                    JobService.refresh_job_features(existing_job.id)
                    count += 1
                except Exception as e:
                    print(f"Error refreshing features for job '{row['job_title']}': {e}")
                continue
                
            description = f"{row['summary']}\n\nResponsibilities:\n{row['responsibilities']}\n\nQualifications:\n{row['qualifications']}"
            
            try:
                JobService.create_job(
                    title=row['job_title'],
                    description=description,
                    domain=row['job_function'] if row['job_function'] else "General",
                    company=row['company'],
                    location=row['location'],
                    job_url=row['url']
                )
                count += 1
                if count % 10 == 0:
                    print(f"Imported {count} jobs...")
            except Exception as e:
                print(f"Error importing job '{row['job_title']}': {e}")
                
        print(f"Successfully imported {count} new jobs.")

if __name__ == "__main__":
    csv_file = os.path.join('Data', 'intermediate', '01_linkedin_jobs_egypt.csv')
   
    populate_jobs(csv_file, limit=200)
