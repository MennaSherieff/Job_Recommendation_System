from pathlib import Path as FilePath
from docx import Document
import uuid
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
import os
from models import User
from dotenv import load_dotenv

load_dotenv()

def register_routes(app,db,bcrypt):

    
    @app.route('/')
    def home():
        return render_template('home.html')

    # def save_raw_cv(text):
    #     cv_id = str(uuid.uuid4())
    #     path = FilePath("storage/cvs")
    #     path.mkdir(parents=True, exist_ok=True)


    #     file_path = path / f"{cv_id}.txt"
    #     file_path.write_text(text, encoding="utf-8") 

    #     return cv_id
    
    @app.route('/upload', methods=['GET','POST'])
    def upload():
        if request.method == 'POST':
            cv_file = request.files['cv_file']
            doc = Document(cv_file)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
            # save_raw_cv(text)
        
        return render_template('upload.html')
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
        
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for('home'))
