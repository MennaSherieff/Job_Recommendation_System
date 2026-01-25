from pathlib import Path as FilePath
from docx import Document
import uuid
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from pipeline.feature_extraction import clean_text
import os
from models import CV, User, Recommendation
from dotenv import load_dotenv

load_dotenv()

def register_routes(app,db,bcrypt):

    
    @app.route('/')
    def home():
        return render_template('home.html')

    def save_raw_cv(text):
        cv_id = str(uuid.uuid4())
        path = FilePath("storage/cvs")
        path.mkdir(parents=True, exist_ok=True)


        file_path = path / f"{cv_id}.txt"
        file_path.write_text(text, encoding="utf-8") 

        return (cv_id,file_path)
    
    @app.route('/upload', methods=['GET','POST'])
    @login_required
    def upload():
        if request.method == 'POST':
            cv_file = request.files.get('cv_file')

            if not cv_file:
                flash("No CV file selected.", "error")
                return redirect(request.url)
            
            # read cv
            try:
                doc = Document(cv_file)
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                flash(f"Error reading CV file: {str(e)}", "error")
                return redirect(request.url)

            cleaned_text = clean_text(text)
            
            # save cv in storage
            saved_file = save_raw_cv(cleaned_text)
            cv = CV(cv_file_path=saved_file[1], user_id=current_user.id)
            db.session.add(cv)
            db.session.commit()

            # Process CV and extract features using service
            from services.cv_service import CVService
            
            try:
                # Extract features from CV
                CVService.process_cv(cv.id)
                
                flash("CV uploaded and processed successfully! Now upload a video to get your job matches.", "success")
                return redirect(url_for('upload'))
                
            except Exception as e:
                flash(f"Error processing CV: {str(e)}", "error")
                return redirect(request.url)
        
        return render_template('upload.html')

    @app.route('/upload_video', methods=['POST'])
    @login_required
    def upload_video():
        video_file = request.files.get('video_file')
        
        if not video_file:
            flash("No video file selected.", "error")
            return redirect(url_for('upload'))
            
        from services.video_service import VideoService
        from services.recommendation_service import RecommendationService
        
        try:
            # Save video
            video_id, file_path = VideoService.save_video(current_user.id, video_file)
            
            # Process video (extract real features)
            video_feature = VideoService.process_video(current_user.id, video_id, file_path)
            
            # Check if user has a completed CV
            cv = CV.query.filter_by(user_id=current_user.id, status='completed').order_by(CV.uploaded_at.desc()).first()
            
            if cv:
                # Generate job recommendations using the FRESH video feature ID to avoid stale caching
                recommendations = RecommendationService.generate_recommendations(
                    user_id=current_user.id,
                    cv_id=cv.id,
                    top_n=10,
                    video_feature_id=video_feature.id
                )
                flash(f"Video processed! Found {len(recommendations)} job matches based on your profile.", "success")
                return redirect(url_for('recommendations'))
            else:
                flash("Video uploaded successfully! Please upload your CV to get job matches.", "success")
                return redirect(url_for('upload'))
            
        except Exception as e:
            flash(f"Error uploading video: {str(e)}", "error")
            return redirect(url_for('upload'))

    @app.route('/delete_cv/<int:cv_id>', methods=['POST'])
    @login_required
    def delete_cv(cv_id):
        from services.cv_service import CVService
        
        if CVService.delete_cv(cv_id, current_user.id):
            flash("CV and associated data deleted successfully.", "success")
        else:
            flash("Error: CV not found or could not be deleted.", "error")
            
        return redirect(url_for('upload'))

    @app.route('/manual_poc', methods=['GET', 'POST'])
    @login_required
    def manual_poc():
        if request.method == 'POST':
            cv_skills = request.form.get('cv_skills', '').split(',')
            job_skills = request.form.get('job_skills', '').split(',')
            domain = request.form.get('domain', 'IT')
            
            from services.recommendation_service import RecommendationService
            
            try:
                # Generate a manual match for POC
                result = RecommendationService.generate_manual_match(
                    cv_skills=[s.strip() for s in cv_skills if s.strip()],
                    job_skills=[s.strip() for s in job_skills if s.strip()],
                    domain=domain
                )
                return render_template('manual_poc.html', result=result)
            except Exception as e:
                flash(f"Error in manual POC: {str(e)}", "error")
                return redirect(url_for('manual_poc'))
                
        return render_template('manual_poc.html')
    
    #!-----------------------------------------------------------Authentication -------------------------------------------------
    @app.route("/register", methods=['GET', 'POST'])
    def register():

        if request.method == 'GET':
            return render_template('register.html', css_file='register.css')

        # POST
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #  Check empty fields
        if not all([username, email,password, confirm_password]):
            return render_template("register.html", css_file='register.css', error="All fields are required.")

        #  Check password match
        if password != confirm_password:
            return render_template("register.html", css_file='register.css', error="Passwords do not match.")

        #  Check if email already exists
        if User.query.filter_by(email=email).first():
            return render_template("register.html", css_file='register.css', error="Email is already registered.")
        #  Check if username already exists
        if User.query.filter_by(user_name=username).first():
            return render_template("register.html", css_file='register.css', error="Username is already taken.")

        #  Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        #  Create user
        new_user = User(
            user_name=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html', css_file='login.css')

        # POST
        username = request.form.get('username')
        password = request.form.get('password')

        # Check empty fields
        if not username or not password:
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Both username and password are required."
            )

        # Find user by username
        user = User.query.filter_by(user_name=username).first()

        if not user:
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Invalid username or password."
            )

        # Check password
        if not bcrypt.check_password_hash(user.password, password):
            return render_template(
                "login.html", 
                css_file='login.css', 
                error="Invalid username or password."
            )

        # Login success
        login_user(user)
        return redirect(url_for('home'))
    
    @app.route('/recommendations')
    @login_required
    def recommendations():
        """Display job recommendations for the current user."""
        from services.recommendation_service import RecommendationService
        
        # Get user's recommendations
        recommendations = RecommendationService.get_user_recommendations(
            user_id=current_user.id,
            limit=20
        )
        
        return render_template('recommendations.html', recommendations=recommendations)
    
    @app.route('/job/<int:job_id>')
    @login_required
    def job_details(job_id):
        """Display detailed job information with skill matching."""
        from services.job_service import JobService
        from services.recommendation_service import RecommendationService
        
        # Get job details
        job = JobService.get_job(job_id)
        if not job:
            flash("Job not found.", "error")
            return redirect(url_for('recommendations'))
        
        # Try to find existing recommendation for this job
        recommendation = Recommendation.query.filter_by(
            user_id=current_user.id,
            job_id=job_id
        ).first()
        
        recommendation_details = None
        if recommendation:
            recommendation_details = RecommendationService.get_recommendation_details(recommendation.id)
        
        return render_template('job_details.html', job=job, recommendation=recommendation_details)
        
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for('home'))
        