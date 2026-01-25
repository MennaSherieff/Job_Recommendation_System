from flask import Flask, flash, redirect, url_for  
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
db = SQLAlchemy()

def create_app():

    load_dotenv()
    app = Flask(__name__, template_folder='templates', static_folder='static')
    password = "password123"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:{password}@localhost:3306/recommendation_system_db"
  
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")  # Change this to a secure secret key in production

    db.init_app(app)


    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Make sure this matches your login route
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'error'

    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    bcrypt = Bcrypt(app)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        from flask import session
        session.clear()  # Clear any existing session data
        flash("You must login first.", "error")
        return redirect(url_for('login'))
    
    from route import register_routes
    register_routes(app, db,bcrypt)
    migrate = Migrate(app,db)

    return app

    
